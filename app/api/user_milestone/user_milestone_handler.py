from typing import Optional
from app.common.validators import validate_uuid4
from app.database.services import user_milestone_service
from app.domain_types.miscellaneous.response_model import ResponseModel
from app.domain_types.schemas.user_milestone import UserMilestoneResponseModel, UserMilestoneSearchResults
from app.telemetry.tracing import trace_span

###############################################################################

@trace_span("handler: create_user_milestone")
def create_user_milestone_(model, db_session):
    try:
        user_milestone = user_milestone_service.create_user_milestone(db_session, model)
        message = "User milestone created successfully"
        resp = ResponseModel[UserMilestoneResponseModel](Message=message, Data=user_milestone)
        return resp
    except Exception as e:
        db_session.rollback()
        db_session.close()
        raise e
    finally:
        db_session.close()

@trace_span("handler: get_user_milestone_by_id")
def get_user_milestone_by_id_(id, db_session):
    try:
        user_milestone_id = validate_uuid4(id)
        user_milestone = user_milestone_service.get_user_milestone_by_id(db_session, user_milestone_id)
        message = "User milestone retrieved successfully"
        resp = ResponseModel[UserMilestoneResponseModel](Message=message, Data=user_milestone)
        return resp
    except Exception as e:
        db_session.rollback()
        db_session.close()
        raise e
    finally:
        db_session.close()

@trace_span("handler: update_user_milestone")
def update_user_milestone_(id, model, db_session):
    try:
        user_milestone_id = validate_uuid4(id)
        user_milestone = user_milestone_service.update_user_milestone(db_session, user_milestone_id, model)
        message = "User milestone updated successfully"
        resp = ResponseModel[UserMilestoneResponseModel](Message=message, Data=user_milestone)
        return resp
    except Exception as e:
        db_session.rollback()
        db_session.close()
        raise e
    finally:
        db_session.close()

@trace_span("handler: delete_user_milestone")
def delete_user_milestone_(id, db_session):
    try:
        user_milestone_id = validate_uuid4(id)
        user_milestone = user_milestone_service.delete_user_milestone(db_session, user_milestone_id)
        message = "User milestone deleted successfully"
        resp = ResponseModel[bool](Message=message, Data=user_milestone)
        return resp
    except Exception as e:
        db_session.rollback()
        db_session.close()
        raise e
    finally:
        db_session.close()

@trace_span("handler: search_user_milestones")
def search_user_milestones_(filter, db_session):
    try:
        user_milestones = user_milestone_service.search_user_milestones(db_session, filter)
        message = "User milestones retrieved successfully"
        resp = ResponseModel[UserMilestoneSearchResults](Message=message, Data=user_milestones)
        return resp
    except Exception as e:
        db_session.rollback()
        db_session.close()
        raise e
    finally:
        db_session.close()
