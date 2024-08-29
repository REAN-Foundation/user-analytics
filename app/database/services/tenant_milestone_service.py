import datetime as dt
import json
import uuid
from app.common.utils import print_colorized_json
from app.database.models.tenant import Tenant
from sqlalchemy.orm import Session
from sqlalchemy import func, asc, desc
from app.database.models.tenant_milestone import TenantMilestone
from app.domain_types.miscellaneous.exceptions import Conflict, NotFound
from app.domain_types.schemas.tenant_milestone import TenantMilestoneCreateModel, TenantMilestoneResponseModel, TenantMilestoneSearchFilter, TenantMilestoneSearchResults, TenantMilestoneUpdateModel
from app.telemetry.tracing import trace_span

###############################################################################

@trace_span("service: create_tenant_milestone")
def create_tenant_milestone(session: Session, model: TenantMilestoneCreateModel) -> TenantMilestoneResponseModel:
    tenant_milestone = session.query(TenantMilestone).filter(
        TenantMilestone.MilestoneName == str(model.MilestoneName),
        TenantMilestone.TenantId == str(model.TenantId)
    ).first()
    if tenant_milestone is not None:
        raise Conflict(f"Tenant milestone with name `{model.MilestoneName}` and tenant with id {model.TenantId} already exists!")

    model_dict = model.dict()
    db_model = TenantMilestone(**model_dict)
    db_model.Attributes = json.dumps(model.Attributes)
    db_model.UpdatedAt = dt.datetime.now()

    session.add(db_model)
    session.commit()
    temp = session.refresh(db_model)

    tenant_milestone = db_model
    tenant_milestone.Attributes = json.loads(tenant_milestone.Attributes)
    return tenant_milestone.__dict__

@trace_span("service: get_tenant_milestone_by_id")
def get_tenant_milestone_by_id(session: Session, tenant_milestone_id: str) -> TenantMilestoneResponseModel:
    tenant_milestone = session.query(TenantMilestone).filter(TenantMilestone.id == tenant_milestone_id).first()
    if not tenant_milestone:
        raise NotFound(f"Tenant milestone with id {tenant_milestone_id} not found")
    tenant_milestone.Attributes = json.loads(tenant_milestone.Attributes)
    return tenant_milestone.__dict__

@trace_span("service: update_tenant_milestone")
def update_tenant_milestone(session: Session, tenant_milestone_id: str, model: TenantMilestoneUpdateModel) -> TenantMilestoneResponseModel:
    tenant_milestone = session.query(TenantMilestone).filter(TenantMilestone.id == tenant_milestone_id).first()
    if not tenant_milestone:
        raise NotFound(f"Tenant milestone with id {tenant_milestone_id} not found")
    update_data = model.dict(exclude_unset=True)
    update_data["UpdatedAt"] = dt.datetime.now()
    update_data["Attributes"] = json.dumps(model.Attributes)
    session.query(TenantMilestone).filter(TenantMilestone.id == tenant_milestone_id).update(update_data, synchronize_session="auto")
    session.commit()
    session.refresh(tenant_milestone)
    tenant_milestone.Attributes = json.loads(tenant_milestone.Attributes)
    return tenant_milestone.__dict__

@trace_span("service: delete_tenant_milestone")
def delete_tenant_milestone(session: Session, tenant_milestone_id: str) -> bool:
    tenant_milestone = session.query(TenantMilestone).filter(TenantMilestone.id == tenant_milestone_id).first()
    if not tenant_milestone:
        raise NotFound(f"Tenant milestone with id {tenant_milestone_id} not found")
    session.delete(tenant_milestone)
    session.commit()
    return True

@trace_span("service: search_tenant_milestones")
def search_tenant_milestones(session: Session, filter: TenantMilestoneSearchFilter) -> TenantMilestoneSearchResults:

    query = session.query(TenantMilestone)

    if filter.MilestoneName:
        query = query.filter(TenantMilestone.MilestoneName.like(f'%{filter.MilestoneName}%'))
    if filter.MilestoneCategory:
        query = query.filter(TenantMilestone.MilestoneCategory.like(f'%{filter.MilestoneCategory}%'))
    if filter.TenantId:
        query = query.filter(TenantMilestone.TenantId == filter.TenantId)
    if filter.FromDate:
        query = query.filter(TenantMilestone.Timestamp >= filter.FromDate)
    if filter.ToDate:
        query = query.filter(TenantMilestone.Timestamp <= filter.ToDate)

    if filter.OrderBy == None:
        filter.OrderBy = "CreatedAt"
    else:
        if not hasattr(TenantMilestone, filter.OrderBy):
            filter.OrderBy = "CreatedAt"
    orderBy = getattr(TenantMilestone, filter.OrderBy)

    if filter.OrderByDescending:
        query = query.order_by(desc(orderBy))
    else:
        query = query.order_by(asc(orderBy))

    query = query.offset(filter.PageIndex * filter.ItemsPerPage).limit(filter.ItemsPerPage)
    tenant_milestones = query.all()
    items = list(map(lambda x: x.__dict__, tenant_milestones))
    for item in items:
        item["Attributes"] = json.loads(item["Attributes"])
    results = TenantMilestoneSearchResults(
        TotalCount=len(tenant_milestones),
        ItemsPerPage=filter.ItemsPerPage,
        PageIndex=filter.PageIndex,
        OrderBy=filter.OrderBy,
        OrderByDescending=filter.OrderByDescending,
        Items=items
    )
    return results
