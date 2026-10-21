import json
from enum import Enum
from pydantic import ValidationError
from app.common.logger import logger
from app.domain_types.schemas.event_message import EventMessage, MessageEventType, UserDeleteEventPayload

###############################################################################

class Outcome(str, Enum):
    ACK   = "ack"    
    RETRY = "retry"  

class EventHandler:

    @staticmethod
    def process(raw_body: str) -> Outcome:
        try:
            event = EventMessage.model_validate(json.loads(raw_body))
        except (json.JSONDecodeError, ValidationError, TypeError) as e:
            logger.error(f"Discarding malformed event message: {e}")
            return Outcome.ACK

        logger.info(f"Received {event.EventType} event {event.EventId}")
        try:
            if event.EventType == MessageEventType.USER_DELETE.value:
                EventHandler.handle_user_deletion(event)
            else:
                logger.warning(f"No handler found for event type: {event.EventType}, skipping event {event.EventId}")
                return Outcome.ACK
        except Exception as e:
            logger.error(f"Handler error for {event.EventType} event {event.EventId}: {e}")
            return Outcome.RETRY

        logger.info(f"Processed {event.EventType} event {event.EventId} successfully")
        return Outcome.ACK

    @staticmethod
    def handle_user_deletion(event: EventMessage) -> None:
        from app.database.database_accessor import get_db_session
        from app.database.services.user_service import delete_user_data
        from app.modules.data_sync.data_synchronizer import DataSynchronizer

        try:
            payload = UserDeleteEventPayload.model_validate(event.Payload or {})
        except ValidationError as e:
            logger.warning(f"Invalid payload for user deletion event {event.EventId}: {e}")
            return
        if not payload.PatientUserId:
            logger.warning(f"Patient user id is required for user deletion event {event.EventId}")
            return

        session = get_db_session()
        try:
            counts = delete_user_data(session, payload.PatientUserId)
        finally:
            session.close()
        DataSynchronizer._user_cache.delete(payload.PatientUserId)

        logger.info(
            f"Deleted analytics data for user {payload.PatientUserId} "
            f"(TenantId={payload.TenantId}, TenantName={payload.TenantName}): {counts}")
