from app.common.utils import validate_uuid4
from app.database.services import cohort_service
from app.domain_types.miscellaneous.response_model import ResponseModel
from app.domain_types.schemas.cohort import CohortResponseModel, CohortSearchResults
from app.telemetry.tracing import trace_span

###############################################################################

@trace_span("handler: create_cohort")
def create_cohort_(model, db_session):
    try:
        cohort = cohort_service.create_cohort(db_session, model)
        message = "Cohort created successfully"
        resp = ResponseModel[CohortResponseModel](
            Message=message, Data=cohort)
        return resp
    except Exception as e:
        print(e)
        db_session.rollback()
        raise e
    finally:
        db_session.close()

@trace_span("handler: get_cohort_by_id")
def get_cohort_by_id_(id, db_session):
    try:
        cohort_id = validate_uuid4(id)
        cohort = cohort_service.get_cohort_by_id(db_session, cohort_id)
        message = "Cohort retrieved successfully"
        resp = ResponseModel[CohortResponseModel](
            Message=message, Data=cohort)
        return resp
    except Exception as e:
        print(e)
        db_session.rollback()
        raise e
    finally:
        db_session.close()

@trace_span("handler: update_cohort")
def update_cohort_(id, model, db_session):
    try:
        cohort_id = validate_uuid4(id)
        cohort = cohort_service.update_cohort(db_session, cohort_id, model)
        message = "Cohort updated successfully"
        resp = ResponseModel[CohortResponseModel](Message=message, Data=cohort)
        return resp
    except Exception as e:
        print(e)
        db_session.rollback()
        raise e
    finally:
        db_session.close()

@trace_span("handler: delete_cohort")
def delete_cohort_(id, db_session):
    try:
        cohort_id = validate_uuid4(id)
        deleted = cohort_service.delete_cohort(db_session, cohort_id)
        message = "Cohort deleted successfully"
        resp = ResponseModel[bool](Message=message, Data=deleted)
        return resp
    except Exception as e:
        print(e)
        db_session.rollback()
        raise e
    finally:
        db_session.close()

@trace_span("handler: search_cohorts")
def search_cohorts_(filter, db_session):
    try:
        cohorts = cohort_service.search_cohorts(db_session, filter)
        message = "cohorts retrieved successfully"
        resp = ResponseModel[CohortSearchResults](Message=message, Data=cohorts)
        return resp
    except Exception as e:
        db_session.rollback()
        db_session.close()
        raise e
    finally:
        db_session.close()

