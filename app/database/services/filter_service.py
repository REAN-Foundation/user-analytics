import datetime as dt
import uuid
# from fastapi import HTTPException, Query, Body
from app.common.utils import print_colorized_json
from app.database.models.filter import Filter
from app.domain_types.miscellaneous.exceptions import Conflict, NotFound
from app.domain_types.schemas.filter import FilterCreateModel, FilterResponseModel, FilterUpdateModel, FilterSearchFilter, FilterSearchResults
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc
from app.telemetry.tracing import trace_span

@trace_span("service: create_filter")
def create_filter(session: Session, model: FilterCreateModel) -> FilterResponseModel:
    model_dict = model.dict()
    db_model = Filter(**model_dict)
    db_model.UpdatedAt = dt.datetime.now()
    session.add(db_model)
    session.commit()
    temp = session.refresh(db_model)
    filter = db_model

    return filter.__dict__

@trace_span("service: get_filter_by_id")
def get_filter_by_id(session: Session, filter_id: str) -> FilterResponseModel:
    filter = session.query(Filter).filter(Filter.id == filter_id).first()
    if not filter:
        raise NotFound(f"Filter with id {filter_id} not found")
    return filter.__dict__

@trace_span("service: update_filter")
def update_filter(session: Session, filter_id: str, model: FilterUpdateModel) -> FilterResponseModel:
    filter = session.query(Filter).filter(Filter.id == filter_id).first()
    if not filter:
        raise NotFound(f"Filter with id {filter_id} not found")

    update_data = model.dict(exclude_unset=True)
    update_data["UpdatedAt"] = dt.datetime.now()
    session.query(Filter).filter(Filter.id == filter_id).update(
        update_data, synchronize_session="auto")

    session.commit()
    session.refresh(filter)
    return filter.__dict__

@trace_span("service: search_filters")
def search_filters(session: Session, filter: FilterSearchFilter) -> FilterSearchResults:

    query = session.query(Filter)
    if filter.Name:
        query = query.filter(Filter.Name.like(f'%{filter.Name}%'))
    # if filter.Description:
    #     query = query.filter(Filter.Description.like(f'%{filter.Description}%'))
    if filter.OwnerId:
        query = query.filter(Filter.OwnerId == filter.OwnerId)
    if filter.UserId:
        query = query.filter(Filter.UserId == filter.UserId)
    if filter.TenantId:
        query = query.filter(Filter.TenantId == filter.TenantId)

    if filter.OrderBy == None:
        filter.OrderBy = "CreatedAt"
    else:
        if not hasattr(Filter, filter.OrderBy):
            filter.OrderBy = "CreatedAt"
    orderBy = getattr(Filter, filter.OrderBy)

    if filter.OrderByDescending:
        query = query.order_by(desc(orderBy))
    else:
        query = query.order_by(asc(orderBy))

    query = query.offset(filter.PageIndex * filter.ItemsPerPage).limit(filter.ItemsPerPage)

    filters = query.all()

    items = list(map(lambda x: x.__dict__, filters))

    results = FilterSearchResults(
        TotalCount=len(filters),
        ItemsPerPage=filter.ItemsPerPage,
        PageIndex=filter.PageIndex,
        OrderBy=filter.OrderBy,
        OrderByDescending=filter.OrderByDescending,
        Items=items
    )

    return results

@trace_span("service: delete_filter")
def delete_filter(session: Session, filter_id: str):
    filter = session.query(Filter).filter(Filter.id == filter_id).first()
    if not filter:
        raise NotFound(f"Filter with id {filter_id} not found")
    session.delete(filter)
    session.commit()
    return True
