from app.common.utils import validate_uuid4
from app.database.services import filter_service
from app.domain_types.miscellaneous.response_model import ResponseModel
from app.domain_types.schemas.filter import FilterResponseModel, FilterSearchResults
from app.telemetry.tracing import trace_span

@trace_span("handler: create_filter")
def create_filter_(model, db_session):
    try:
        filter = filter_service.create_filter(db_session, model)
        message = "Filter created successfully"
        resp = ResponseModel[FilterResponseModel](Message=message, Data=filter)
        return resp
    except Exception as e:
        db_session.rollback()
        db_session.close()
        raise e
    finally:
        db_session.close()

@trace_span("handler: get_filter_by_id")
def get_filter_by_id_(id, db_session):
    try:
        filter_id = validate_uuid4(id)
        filter = filter_service.get_filter_by_id(db_session, filter_id)
        message = "Filter retrieved successfully"
        resp = ResponseModel[FilterResponseModel](Message=message, Data=filter)
        return resp
    except Exception as e:
        db_session.rollback()
        db_session.close()
        raise e
    finally:
        db_session.close()


@trace_span("handler: update_filter")
def update_filter_(id, model, db_session):
    try:
        filter_id = validate_uuid4(id)
        filter = filter_service.update_filter(db_session, filter_id, model)
        message = "Filter updated successfully"
        resp = ResponseModel[FilterResponseModel](Message=message, Data=filter)
        return resp
    except Exception as e:
        db_session.rollback()
        db_session.close()
        raise e
    finally:
        db_session.close()

@trace_span("handler: delete_filter")
def delete_filter_(id, db_session):
    try:
        filter_id = validate_uuid4(id)
        filter = filter_service.delete_filter(db_session, filter_id)
        message = "Filter deleted successfully"
        resp = ResponseModel[bool](Message=message, Data=filter)
        return resp
    except Exception as e:
        db_session.rollback()
        db_session.close()
        raise e
    finally:
        db_session.close()

@trace_span("handler: search_filters")
def search_filters_(filter, db_session):
    try:
        filters = filter_service.search_filters(db_session, filter)
        message = "Filters retrieved successfully"
        resp = ResponseModel[FilterSearchResults](Message=message, Data=filters)
        return resp
    except Exception as e:
        db_session.rollback()
        db_session.close()
        raise e
    finally:
        db_session.close()
