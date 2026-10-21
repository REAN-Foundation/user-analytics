import logging
import threading
import pika
from app.common.logger import logger
from app.config.config import get_settings
from app.modules.events.event_consumer_interface import IEventConsumer
from app.modules.events.event_handler import EventHandler, Outcome

###############################################################################

logging.getLogger("pika").setLevel(logging.CRITICAL)

class RabbitMqEventConsumer(IEventConsumer):

    _max_backoff_seconds = 30

    def __init__(self):
        settings = get_settings()
        self._queue_name = settings.EVENT_QUEUE_NAME
        self._connection_string = settings.RABBITMQ_CONNECTION_STRING
        self._connection = None
        self._channel = None
        self._thread = None
        self._stop_event = threading.Event()

    def start_listening(self) -> None:
        if self._thread and self._thread.is_alive():
            logger.warning(f"Consumer for {self._queue_name} already listening")
            return
        if not self._queue_name or not self._connection_string:
            logger.error("EVENT_QUEUE_NAME and RABBITMQ_CONNECTION_STRING must be set for the RabbitMQ consumer")
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._consume_loop, name="rabbitmq-event-consumer", daemon=True)
        self._thread.start()

    def stop_listening(self) -> None:
        self._stop_event.set()
        connection, channel = self._connection, self._channel
        if connection and connection.is_open and channel:
            try:
                # pika connections are not thread safe; stop consuming on the consumer thread
                connection.add_callback_threadsafe(channel.stop_consuming)
            except Exception as e:
                logger.error(f"Error stopping consumer for {self._queue_name}: {e}")

    def close(self) -> None:
        self.stop_listening()
        if self._thread:
            self._thread.join(timeout=10)
            self._thread = None
        logger.info(f"Consumer connection closed for queue: {self._queue_name}")

    def _consume_loop(self) -> None:
        backoff = 1
        while not self._stop_event.is_set():
            try:
                self._connection = pika.BlockingConnection(pika.URLParameters(self._connection_string))
                self._channel = self._connection.channel()
                self._channel.basic_qos(prefetch_count=1)
                self._channel.queue_declare(queue=self._queue_name, passive=True)
                self._channel.basic_consume(queue=self._queue_name, on_message_callback=self._on_message, auto_ack=False)
                logger.info(f"Started consuming events from existing queue: {self._queue_name}")
                backoff = 1
                self._channel.start_consuming()
            except Exception as e:
                if self._stop_event.is_set():
                    break
                logger.error(f"Consumer connection error on {self._queue_name}: {type(e).__name__} {e}. Reconnecting in {backoff}s")
                self._stop_event.wait(backoff)
                backoff = min(backoff * 2, self._max_backoff_seconds)
            finally:
                self._close_connection()

    def _on_message(self, channel, method, properties, body: bytes) -> None:
        outcome = EventHandler.process(body.decode("utf-8", errors="replace"))
        if outcome == Outcome.ACK:
            channel.basic_ack(delivery_tag=method.delivery_tag)
        else:
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def _close_connection(self) -> None:
        try:
            if self._connection and self._connection.is_open:
                self._connection.close()
        except Exception as e:
            logger.error(f"Error closing consumer connection: {e}")
        finally:
            self._connection = None
            self._channel = None
