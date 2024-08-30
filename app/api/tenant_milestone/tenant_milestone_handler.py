from typing import Optional
from app.common.validators import validate_uuid4
from app.database.services import tenant_milestone_service
from app.domain_types.miscellaneous.response_model import ResponseModel
from app.domain_types.schemas.tenant_milestone import TenantMilestoneResponseModel, TenantMilestoneSearchResults
from app.telemetry.tracing import trace_span

###############################################################################

@trace_span("handler: create_tenant_milestone")
def create_tenant_milestone_(model, db_session):
    try:
        tenant_milestone = tenant_milestone_service.create_tenant_milestone(db_session, model)
        message = "Tenant milestone created successfully"
        resp = ResponseModel[TenantMilestoneResponseModel](Message=message, Data=tenant_milestone)
        return resp
    except Exception as e:
        db_session.rollback()
        db_session.close()
        raise e
    finally:
        db_session.close()

@trace_span("handler: get_tenant_milestone_by_id")
def get_tenant_milestone_by_id_(id, db_session):
    try:
        tenant_milestone_id = validate_uuid4(id)
        tenant_milestone = tenant_milestone_service.get_tenant_milestone_by_id(db_session, tenant_milestone_id)
        message = "Tenant milestone retrieved successfully"
        resp = ResponseModel[TenantMilestoneResponseModel](Message=message, Data=tenant_milestone)
        return resp
    except Exception as e:
        db_session.rollback()
        db_session.close()
        raise e
    finally:
        db_session.close()

@trace_span("handler: update_tenant_milestone")
def update_tenant_milestone_(id, model, db_session):
    try:
        tenant_milestone_id = validate_uuid4(id)
        tenant_milestone = tenant_milestone_service.update_tenant_milestone(db_session, tenant_milestone_id, model)
        message = "Tenant milestone updated successfully"
        resp = ResponseModel[TenantMilestoneResponseModel](Message=message, Data=tenant_milestone)
        return resp
    except Exception as e:
        db_session.rollback()
        db_session.close()
        raise e
    finally:
        db_session.close()

@trace_span("handler: delete_tenant_milestone")
def delete_tenant_milestone_(id, db_session):
    try:
        tenant_milestone_id = validate_uuid4(id)
        tenant_milestone = tenant_milestone_service.delete_tenant_milestone(db_session, tenant_milestone_id)
        message = "Tenant milestone deleted successfully"
        resp = ResponseModel[bool](Message=message, Data=tenant_milestone)
        return resp
    except Exception as e:
        db_session.rollback()
        db_session.close()
        raise e
    finally:
        db_session.close()

@trace_span("handler: search_tenant_milestones")
def search_tenant_milestones_(filter, db_session):
    try:
        tenant_milestones = tenant_milestone_service.search_tenant_milestones(db_session, filter)
        message = "Tenant milestones retrieved successfully"
        resp = ResponseModel[TenantMilestoneSearchResults](Message=message, Data=tenant_milestones)
        return resp
    except Exception as e:
        db_session.rollback()
        db_session.close()
        raise e
    finally:
        db_session.close()
