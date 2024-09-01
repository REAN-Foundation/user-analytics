import datetime as dt
import json
from app.common.utils import print_colorized_json
from app.database.models.user import User
from app.domain_types.schemas.user import UserCreateModel, UserMetadataUpdateModel, UserResponseModel, UserSearchFilter, UserSearchResults
from sqlalchemy.orm import Session
from app.domain_types.miscellaneous.exceptions import Conflict, NotFound
from sqlalchemy import asc, desc
from app.telemetry.tracing import trace_span

###############################################################################

@trace_span("service: create_user")
def create_user(session: Session, model: UserCreateModel) -> UserResponseModel:
    user = session.query(User).filter(User.id == str(model.id)).first()
    if user != None:
        raise Conflict(f"User with id `{model.id}` already exists!")
    model_dict = model.dict()
    db_model = User(**model_dict)
    session.add(db_model)
    session.commit()
    temp = session.refresh(db_model)
    user = db_model
    user.Attributes = json.loads(user.Attributes)
    print_colorized_json(user)
    return user.__dict__


@trace_span("service: get_user_by_id")
def get_user_by_id(session: Session, user_id: str) -> UserResponseModel:
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFound(f"User with id {user_id} not found")
    # user.Attributes = json.loads(user.Attributes)
    print_colorized_json(user)
    return user.__dict__

@trace_span("service: update_user_metadata")
def update_user_metadata(session: Session, user_id: str, model: UserMetadataUpdateModel) -> bool:
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFound(f"User with id {user_id} not found")

    update_data = model.dict(exclude_unset=True)
    if model.Attributes:
        update_data["Attributes"] = json.dumps(model.Attributes)

    session.query(User).filter(User.id == user_id).update(
        update_data, synchronize_session="auto")

    session.commit()
    session.refresh(user)

    user.Attributes = json.loads(user.Attributes)
    print_colorized_json(user)

    return True

@trace_span("service: search_users")
def search_users(session: Session, filter: UserSearchFilter) -> UserSearchResults:

    query = session.query(User)

    # if filter.Attribute:
    #     query = query.filter(User.Attributes.like(f'%{filter.Attribute}%'))

    if filter.LastActiveBefore:
        query = query.filter(User.LastActive < filter.LastActiveBefore)
    if filter.LastActiveAfter:
        query = query.filter(User.LastActive > filter.LastActiveAfter)

    if filter.RegisteredBefore:
        query = query.filter(User.RegistrationDate < filter.RegisteredBefore)
    if filter.RegisteredAfter:
        query = query.filter(User.RegistrationDate > filter.RegisteredAfter)

    if filter.OrderBy == None:
        filter.OrderBy = "CreatedAt"
    else:
        if not hasattr(User, filter.OrderBy):
            filter.OrderBy = "CreatedAt"
    orderBy = getattr(User, filter.OrderBy)

    if filter.OrderByDescending:
        query = query.order_by(desc(orderBy))
    else:
        query = query.order_by(asc(orderBy))

    query = query.offset(filter.PageIndex * filter.ItemsPerPage).limit(filter.ItemsPerPage)

    users = query.all()
    items = list(map(lambda x: x.__dict__, users))
    for item in items:
        item["Attributes"] = json.loads(item["Attributes"])

    results = UserSearchResults(
        TotalCount=len(users),
        ItemsPerPage=filter.ItemsPerPage,
        PageIndex=filter.PageIndex,
        OrderBy=filter.OrderBy,
        OrderByDescending=filter.OrderByDescending,
        Items=items
    )

    return results

@trace_span("service: delete_user")
def delete_user(session: Session, user_id: str) -> bool:
    user = session.query(User).get(user_id)
    if not user:
        raise NotFound(f"User with id {user_id} not found")
    update_data = {
        "DeletedAt": dt.datetime.now()
    }
    session.query(User).filter(User.id == user_id).update(
        update_data, synchronize_session="auto")
    session.commit()
    return True
