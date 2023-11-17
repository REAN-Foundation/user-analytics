import datetime as dt
import json
import uuid
from fastapi import HTTPException, Query, Body
from app.common.utils import print_colorized_json
from app.database.database_accessor import LocalSession
from app.database.models.user import User
from app.domain_types.schemas.user import UserCreateModel, UserResponseModel, UserUpdateModel, UserSearchFilter, UserSearchResults
from sqlalchemy.orm import Session
from app.domain_types.miscellaneous.exceptions import Conflict, NotFound
from sqlalchemy import asc, desc, func
from app.telemetry.tracing import trace_span

@trace_span("service: create_user")
def create_user(session: Session, model: UserCreateModel) -> UserResponseModel:
    try:
        model_dict = model.dict()
        db_model = User(**model_dict)
        db_model.Attributes = json.dumps(model.Attributes)
        db_model.UpdatedAt = dt.datetime.now()
        session.add(db_model)
        session.commit()
        temp = session.refresh(db_model)
        user = db_model
        user.Attributes = json.loads(user.Attributes)
        print_colorized_json(user)
        return user.__dict__
    except Exception as e:
        raise Conflict(f"Error creating user: {e.orig}")

@trace_span("service: get_user_by_id")
def get_user_by_id(session: Session, user_id: str) -> UserResponseModel:
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFound(f"User with id {user_id} not found")

    print_colorized_json(user)
    return user.__dict__

@trace_span("service: update_user")
def update_user(session: Session, user_id: str, model: UserUpdateModel) -> UserResponseModel:
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFound(f"User with id {user_id} not found")

    update_data = model.dict(exclude_unset=True)
    update_data["UpdatedAt"] = dt.datetime.now()
    session.query(User).filter(User.id == user_id).update(
        update_data, synchronize_session="auto")

    session.commit()
    session.refresh(user)

    print_colorized_json(user)
    return user.__dict__

@trace_span("service: search_useres")
def search_useres(session: Session, filter: UserSearchFilter) -> UserSearchResults:

    query = session.query(User)

    if filter.Name:
        query = query.filter(User.Name.like(f'%{filter.Name}%'))
    if filter.Email:
        query = query.filter(User.Email.like(f'%{filter.Email}%'))
    if filter.PhoneCode:
        query = query.filter(User.PhoneCode.like(f'%{filter.PhoneCode}%'))
    if filter.Phone:
        query = query.filter(User.Phone.like(f'%{filter.Phone}%'))

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

    useres = query.all()

    items = list(map(lambda x: x.__dict__, useres))

    results = UserSearchResults(
        TotalCount=len(useres),
        ItemsPerPage=filter.ItemsPerPage,
        PageIndex=filter.PageIndex,
        OrderBy=filter.OrderBy,
        OrderByDescending=filter.OrderByDescending,
        Items=items
    )

    return results

@trace_span("service: delete_user")
def delete_user(session: Session, user_id: str) -> UserResponseModel:
    user = session.query(User).get(user_id)
    if not user:
        raise NotFound(f"User with id {user_id} not found")

    session.delete(user)

    session.commit()

    print_colorized_json(user)
    return user.__dict__