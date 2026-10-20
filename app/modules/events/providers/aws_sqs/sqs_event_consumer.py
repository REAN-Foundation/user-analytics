import json
import os
import threading
import boto3
from app.common.logger import logger
from app.config.config import get_settings
from app.modules.events.event_consumer_interface import IEventConsumer
from app.modules.events.event_handler import EventHandler, Outcome

###############################################################################

class AwsSqsEventConsumer(IEventConsumer):

    _max_backoff_seconds = 30

    def __init__(self):
        settings = get_settings()
        self._queue_url = settings.EVENT_QUEUE_URL
        # Read like the S3 storage provider: when unset, boto3 falls back to the default credential chain (e.g. ECS task role)
        self._region = os.getenv("AWS_REGION")
        self._access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self._secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self._polling_interval_sec = settings.SQS_POLLING_INTERVAL_MS / 1000
        self._max_messages = settings.SQS_MAX_MESSAGES
        self._wait_time_seconds = settings.SQS_WAIT_TIME_SECONDS
        self._client = None
        self._thread = None
        self._stop_event = threading.Event()

    def start_listening(self) -> None:
        if self._thread and self._thread.is_alive():
            logger.warning(f"Consumer for {self._queue_url} already listening")
            return
        try:
            self._initialize_connection()
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._poll_loop, name="sqs-event-consumer", daemon=True)
            self._thread.start()
            logger.info(f"Started consuming events from SQS queue: {self._queue_url}")
        except Exception as e:
            logger.error(f"Error starting consumer for {self._queue_url}: {e}")

    def stop_listening(self) -> None:
        self._stop_event.set()

    def close(self) -> None:
        self.stop_listening()
        if self._thread:
            self._thread.join(timeout=self._wait_time_seconds + 5)
            self._thread = None
        if self._client:
            self._client.close()
            self._client = None
        logger.info(f"Consumer SQS client closed for queue: {self._queue_url}")

    def _initialize_connection(self) -> None:
        if not self._queue_url:
            raise ValueError("EVENT_QUEUE_URL is not set")
        self._client = boto3.client(
            "sqs",
            region_name=self._region,
            aws_access_key_id=self._access_key_id,
            aws_secret_access_key=self._secret_access_key,
        )
        result = self._client.get_queue_attributes(
            QueueUrl=self._queue_url,
            AttributeNames=["QueueArn", "ApproximateNumberOfMessages", "VisibilityTimeout"],
        )
        attributes = result.get("Attributes", {})
        logger.info(
            f"Queue validated: {self._queue_url} "
            f"(ARN={attributes.get('QueueArn', 'N/A')}, "
            f"ApproximateMessages={attributes.get('ApproximateNumberOfMessages', '0')}, "
            f"VisibilityTimeout={attributes.get('VisibilityTimeout', 'N/A')}s)")

    def _poll_loop(self) -> None:
        backoff = 1
        while not self._stop_event.is_set():
            try:
                result = self._client.receive_message(
                    QueueUrl=self._queue_url,
                    MaxNumberOfMessages=self._max_messages,
                    WaitTimeSeconds=self._wait_time_seconds,
                    MessageAttributeNames=["All"],
                )
                messages = result.get("Messages", [])
                if messages:
                    logger.info(f"Received {len(messages)} message(s) from queue")
                for message in messages:
                    self._handle_message(message)
                backoff = 1
                self._stop_event.wait(self._polling_interval_sec)
            except Exception as e:
                if self._stop_event.is_set():
                    break
                logger.error(f"Error polling messages from {self._queue_url}: {e}")
                self._stop_event.wait(backoff)
                backoff = min(backoff * 2, self._max_backoff_seconds)

    def _handle_message(self, message: dict) -> None:
        body = self._unwrap_sns_envelope(message.get("Body", ""))
        outcome = EventHandler.process(body)
        if outcome == Outcome.ACK:
            self._client.delete_message(QueueUrl=self._queue_url, ReceiptHandle=message["ReceiptHandle"])
        else:
            logger.warning(f"Message {message.get('MessageId')} will be redelivered")

    @staticmethod
    def _unwrap_sns_envelope(body: str) -> str:
        try:
            parsed = json.loads(body)
        except (json.JSONDecodeError, TypeError):
            return body
        if isinstance(parsed, dict) and parsed.get("Type") == "Notification" and "Message" in parsed:
            return parsed["Message"]
        return body
