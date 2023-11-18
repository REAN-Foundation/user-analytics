from app.common.utils import validate_uuid4
from app.database.services import event_service
from app.domain_types.miscellaneous.response_model import ResponseModel
from app.domain_types.schemas.event import EventResponseModel, EventSearchResults
from app.telemetry.tracing import trace_span

###############################################################################

@trace_span("handler: create_event")
def create_event_(model, db_session):
    try:
        event = event_service.create_event(db_session, model)
        message = "Event created successfully"
        resp = ResponseModel[EventResponseModel](Message=message, Data=event)
        return resp
    except Exception as e:
        db_session.rollback()
        db_session.close()
        raise e
    finally:
        db_session.close()

@trace_span("handler: get_event_by_id")
def get_event_by_id_(id, db_session):
    try:
        event_id = validate_uuid4(id)
        event = event_service.get_event_by_id(db_session, event_id)
        message = "Event retrieved successfully"
        resp = ResponseModel[EventResponseModel](Message=message, Data=event)
        return resp
    except Exception as e:
        db_session.rollback()
        db_session.close()
        raise e
    finally:
        db_session.close()

@trace_span("handler: update_event")
def update_event_(id, model, db_session):
    try:
        event_id = validate_uuid4(id)
        event = event_service.update_event(db_session, event_id, model)
        message = "Event updated successfully"
        resp = ResponseModel[EventResponseModel](Message=message, Data=event)
        return resp
    except Exception as e:
        db_session.rollback()
        db_session.close()
        raise e
    finally:
        db_session.close()

@trace_span("handler: delete_event")
def delete_event_(id, db_session):
    try:
        event_id = validate_uuid4(id)
        deleted = event_service.delete_event(db_session, event_id)
        message = "Event deleted successfully"
        resp = ResponseModel[bool](Message=message, Data=deleted)
        return resp
    except Exception as e:
        db_session.rollback()
        db_session.close()
        raise e
    finally:
        db_session.close()

@trace_span("handler: search_events")
def search_events_(filter, db_session):
    try:
        events = event_service.search_events(db_session, filter)
        message = "Events retrieved successfully"
        resp = ResponseModel[EventSearchResults](Message=message, Data=events)
        return resp
    except Exception as e:
        db_session.rollback()
        db_session.close()
        raise e
    finally:
        db_session.close()
