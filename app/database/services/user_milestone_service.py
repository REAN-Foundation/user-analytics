import datetime as dt
import json
import uuid
from app.common.utils import print_colorized_json
from app.database.models.user import User
from sqlalchemy.orm import Session
from sqlalchemy import func, asc, desc
from app.database.models.user_milestone import UserMilestone
from app.domain_types.miscellaneous.exceptions import Conflict, NotFound
from app.domain_types.schemas.user_milestone import UserMilestoneCreateModel, UserMilestoneResponseModel, UserMilestoneSearchFilter, UserMilestoneSearchResults, UserMilestoneUpdateModel
from app.telemetry.tracing import trace_span

###############################################################################

@trace_span("service: create_user_milestone")
def create_user_milestone(session: Session, model: UserMilestoneCreateModel) -> UserMilestoneResponseModel:
    user_milestone = session.query(UserMilestone).filter(
        UserMilestone.MilestoneName == str(model.MilestoneName),
        UserMilestone.UserId == str(model.UserId)
    ).first()
    if user_milestone is not None:
        raise Conflict(f"User milestone with name `{model.MilestoneName}` and user with id {model.UserId} already exists!")

    user = session.query(User).filter(User.id == model.UserId).first()
    if user is None:
        raise NotFound(f"User with id {model.UserId} not found")
    user_registration_date = user.RegistrationDate.replace(tzinfo=dt.timezone.utc)
    offset_seconds = (model.Timestamp - user_registration_date).total_seconds()
    offset_days = (model.Timestamp - user_registration_date).days

    model_dict = model.dict()
    db_model = UserMilestone(**model_dict)
    db_model.DaysSinceRegistration = offset_days
    db_model.TimeOffsetSinceRegistration = offset_seconds
    db_model.Attributes = json.dumps(model.Attributes)
    db_model.UpdatedAt = dt.datetime.now()

    session.add(db_model)
    session.commit()
    temp = session.refresh(db_model)

    user_milestone = db_model
    user_milestone.Attributes = json.loads(user_milestone.Attributes)
    return user_milestone.__dict__

@trace_span("service: get_user_milestone_by_id")
def get_user_milestone_by_id(session: Session, user_milestone_id: str) -> UserMilestoneResponseModel:
    user_milestone = session.query(UserMilestone).filter(UserMilestone.id == user_milestone_id).first()
    if not user_milestone:
        raise NotFound(f"User milestone with id {user_milestone_id} not found")
    user_milestone.Attributes = json.loads(user_milestone.Attributes)
    return user_milestone.__dict__

@trace_span("service: update_user_milestone")
def update_user_milestone(session: Session, user_milestone_id: str, model: UserMilestoneUpdateModel) -> UserMilestoneResponseModel:
    user_milestone = session.query(UserMilestone).filter(UserMilestone.id == user_milestone_id).first()
    if not user_milestone:
        raise NotFound(f"User milestone with id {user_milestone_id} not found")
    update_data = model.dict(exclude_unset=True)
    update_data["UpdatedAt"] = dt.datetime.now()
    update_data["Attributes"] = json.dumps(model.Attributes)
    session.query(UserMilestone).filter(UserMilestone.id == user_milestone_id).update(update_data, synchronize_session="auto")
    session.commit()
    session.refresh(user_milestone)
    user_milestone.Attributes = json.loads(user_milestone.Attributes)
    return user_milestone.__dict__

@trace_span("service: delete_user_milestone")
def delete_user_milestone(session: Session, user_milestone_id: str) -> bool:
    user_milestone = session.query(UserMilestone).filter(UserMilestone.id == user_milestone_id).first()
    if not user_milestone:
        raise NotFound(f"user_milestone with id {user_milestone_id} not found")
    session.delete(user_milestone)
    session.commit()
    return True

@trace_span("service: search_user_milestones")
def search_user_milestones(session: Session, filter: UserMilestoneSearchFilter) -> UserMilestoneSearchResults:

    query = session.query(UserMilestone)

    if filter.UserId:
        query = query.filter(UserMilestone.UserId == filter.UserId)
    if filter.MilestoneName:
        query = query.filter(UserMilestone.MilestoneName.like(f'%{filter.MilestoneName}%'))
    if filter.MilestoneCategory:
        query = query.filter(UserMilestone.MilestoneCategory.like(f'%{filter.MilestoneCategory}%'))
    if filter.TenantId:
        query = query.filter(UserMilestone.TenantId == filter.TenantId)
    if filter.FromDate:
        query = query.filter(UserMilestone.Timestamp >= filter.FromDate)
    if filter.ToDate:
        query = query.filter(UserMilestone.Timestamp <= filter.ToDate)
    if filter.FromDaysSinceRegistration:
        query = query.filter(UserMilestone.DaysSinceRegistration >= filter.FromDaysSinceRegistration)
    if filter.ToDaysSinceRegistration:
        query = query.filter(UserMilestone.DaysSinceRegistration <= filter.ToDaysSinceRegistration)
    if filter.FromTimeOffsetSinceRegistration:
        query = query.filter(UserMilestone.TimeOffsetSinceRegistration >= filter.FromTimeOffsetSinceRegistration)
    if filter.ToTimeOffsetSinceRegistration:
        query = query.filter(UserMilestone.TimeOffsetSinceRegistration <= filter.ToTimeOffsetSinceRegistration)

    if filter.OrderBy == None:
        filter.OrderBy = "CreatedAt"
    else:
        if not hasattr(UserMilestone, filter.OrderBy):
            filter.OrderBy = "CreatedAt"
    orderBy = getattr(UserMilestone, filter.OrderBy)

    if filter.OrderByDescending:
        query = query.order_by(desc(orderBy))
    else:
        query = query.order_by(asc(orderBy))

    query = query.offset(filter.PageIndex * filter.ItemsPerPage).limit(filter.ItemsPerPage)
    user_milestones = query.all()
    items = list(map(lambda x: x.__dict__, user_milestones))
    for item in items:
        item["Attributes"] = json.loads(item["Attributes"])
    results = UserMilestoneSearchResults(
        TotalCount=len(user_milestones),
        ItemsPerPage=filter.ItemsPerPage,
        PageIndex=filter.PageIndex,
        OrderBy=filter.OrderBy,
        OrderByDescending=filter.OrderByDescending,
        Items=items
    )
    return results
