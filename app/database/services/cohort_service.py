import datetime as dt
import json
import uuid
from app.common.utils import print_colorized_json
from app.database.models.cohort import Cohort
from app.database.models.cohort_users import CohortUser
from app.database.models.user import User
from sqlalchemy.orm import Session
from sqlalchemy import func, asc, desc
from app.domain_types.miscellaneous.exceptions import Conflict, NotFound
from app.domain_types.schemas.cohort import CohortCreateModel, CohortResponseModel, CohortSearchResults, CohortSearchFilter, CohortUpdateModel
from app.telemetry.tracing import trace_span

###############################################################################

@trace_span("service: create_cohort")
def create_cohort(session: Session, model: CohortCreateModel) -> CohortResponseModel:
    cohort = session.query(Cohort).filter(
        Cohort.Name == str(model.Name),
        Cohort.TenantId == str(model.TenantId) 
    ).first()
    if cohort is not None:
        raise Conflict(f"Cohort with name `{model.Name}` and tenant with id {model.TenantId} already exists!")
    model_dict = model.dict()
    db_model = Cohort(**model_dict)
    db_model.Attributes = json.dumps(model.Attributes)
    db_model.UpdatedAt = dt.datetime.now()
    session.add(db_model)
    session.commit()
    temp = session.refresh(db_model)
    cohort = db_model
    cohort.Attributes = json.loads(cohort.Attributes)
    return cohort.__dict__

@trace_span("service: get_cohort_by_id")
def get_cohort_by_id(session: Session, cohort_id: str) -> CohortResponseModel:
    cohort = session.query(Cohort).filter(Cohort.id == cohort_id).first()
    if not cohort:
        raise NotFound(f"cohort with id {cohort_id} not found")
    cohort.Attributes = json.loads(cohort.Attributes)
    return cohort.__dict__

@trace_span("service: update_cohort")
def update_cohort(session: Session, cohort_id: str, model: CohortUpdateModel) -> CohortResponseModel:
    cohort = session.query(Cohort).filter(Cohort.id == cohort_id).first()
    if not cohort:
        raise NotFound(f"Cohort with id {cohort_id} not found")
    update_data = model.dict(exclude_unset=True)
    update_data["UpdatedAt"] = dt.datetime.now()
    update_data["Attributes"] = json.dumps(model.Attributes)
    session.query(Cohort).filter(Cohort.id == cohort_id).update(update_data, synchronize_session="auto")
    session.commit()
    session.refresh(cohort)
    cohort.Attributes = json.loads(cohort.Attributes)
    return cohort.__dict__

@trace_span("service: delete_cohort")
def delete_cohort(session: Session, cohort_id: str) -> bool:
    cohort = session.query(Cohort).filter(Cohort.id == cohort_id).first()
    if not cohort:
        raise NotFound(f"cohort with id {cohort_id} not found")
    session.delete(cohort)
    session.commit()
    return True

@trace_span("service: search_cohorts")
def search_cohorts(session: Session, filter: CohortSearchFilter) -> CohortSearchResults:

    query = session.query(Cohort)

    if filter.Name:
        query = query.filter(Cohort.Name.like(f'%{filter.Name}%'))
    if filter.Description:
        query = query.filter(Cohort.Description.like(f'%{filter.Description}%'))
    if filter.TenantId:
        query = query.filter(Cohort.TenantId == filter.TenantId)
    if filter.OwnerId:
        query = query.filter(Cohort.OwnerId == filter.OwnerId)

    if filter.OrderBy == None:
        filter.OrderBy = "CreatedAt"
    else:
        if not hasattr(Cohort, filter.OrderBy):
            filter.OrderBy = "CreatedAt"
    orderBy = getattr(Cohort, filter.OrderBy)

    if filter.OrderByDescending:
        query = query.order_by(desc(orderBy))
    else:
        query = query.order_by(asc(orderBy))

    query = query.offset(filter.PageIndex * filter.ItemsPerPage).limit(filter.ItemsPerPage)
    cohorts = query.all()
    items = list(map(lambda x: x.__dict__, cohorts))
    for item in items:
        item["Attributes"] = json.loads(item["Attributes"])
    results = CohortSearchResults(
        TotalCount=len(cohorts),
        ItemsPerPage=filter.ItemsPerPage,
        PageIndex=filter.PageIndex,
        OrderBy=filter.OrderBy,
        OrderByDescending=filter.OrderByDescending,
        Items=items
    )
    return results

@trace_span("service: add_user_to_cohort")
def add_user_to_cohort(session: Session, cohort_id: str, user_id: str) -> bool:
    cohort = session.query(Cohort).filter(Cohort.id == cohort_id).first()
    if not cohort:
        raise NotFound(f"Cohort with id {cohort_id} not found")
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFound(f"User with id {user_id} not found")
    cohort_user = session.query(CohortUser).filter(
        CohortUser.CohortId == cohort_id,
        CohortUser.UserId == user_id
    ).first()
    if cohort_user is not None:
        raise Conflict(f"User with id {user_id} already exists in cohort with id {cohort_id}")
    cohort_user = CohortUser(
        CohortId=cohort_id,
        UserId=user_id
    )
    session.add(cohort_user)
    session.commit()
    session.refresh(cohort)
    return True

@trace_span("service: remove_user_from_cohort")
def remove_user_from_cohort(session: Session, cohort_id: str, user_id: str) -> bool:
    cohort = session.query(Cohort).filter(Cohort.id == cohort_id).first()
    if not cohort:
        raise NotFound(f"Cohort with id {cohort_id} not found")
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFound(f"User with id {user_id} not found")
    cohort_user = session.query(CohortUser).filter(
        CohortUser.CohortId == cohort_id,
        CohortUser.UserId == user_id
    ).first()
    if cohort_user is None:
        raise NotFound(f"User with id {user_id} does not exist in cohort with id {cohort_id}")
    session.delete(cohort_user)
    session.commit()
    session.refresh(cohort)
    return True

def get_cohort_users(session: Session, cohort_id: str):
    cohort = session.query(Cohort).filter(Cohort.id == cohort_id).first()
    if not cohort:
        raise NotFound(f"Cohort with id {cohort_id} not found")
    return get_users(session, cohort_id)

def get_users(session: Session, cohort_id: str):
    cohort_users = session.query(CohortUser).filter(CohortUser.CohortId == cohort_id).all()
    users = list(map(lambda x: x.__dict__, cohort_users))
    users_ = []
    for user in users:
        u = session.query(User).filter(User.id == user["UserId"]).first().__dict__
        u_ = {}
        u_["id"]        = u["id"]
        u_["FirstName"] = u["FirstName"]
        u_["LastName"]  = u["LastName"]
        u_["Email"]     = u["Email"]
        u_["Phone"]     = u["PhoneCode"] + "-" + u["Phone"]
        users_.append(u_)
    return users