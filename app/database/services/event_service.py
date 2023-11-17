import datetime as dt
import uuid
from app.common.utils import print_colorized_json
from app.database.models.event import Event
from app.domain_types.miscellaneous.exceptions import Conflict, NotFound
from app.domain_types.schemas.event import EventCreateModel, EventResponseModel, EventUpdateModel, EventSearchFilter, EventSearchResults
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc
from app.telemetry.tracing import trace_span

@trace_span("service: create_event")
def create_event(session: Session, model: EventCreateModel) -> EventResponseModel:
    model_dict = model.dict()
    db_model = Event(**model_dict)
    db_model.UpdatedAt = dt.datetime.now()
    session.add(db_model)
    session.commit()
    temp = session.refresh(db_model)
    event = db_model

    return event.__dict__

@trace_span("service: get_event_by_id")
def get_event_by_id(session: Session, event_id: str) -> EventResponseModel:
    event = session.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise NotFound(f"Event with id {event_id} not found")
    return event.__dict__

@trace_span("service: update_event")
def update_event(session: Session, event_id: str, model: EventUpdateModel) -> EventResponseModel:
    event = session.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise NotFound(f"Event with id {event_id} not found")

    update_data = model.dict(exclude_unset=True)
    update_data["UpdatedAt"] = dt.datetime.now()
    session.query(Event).filter(Event.id == event_id).update(
        update_data, synchronize_session="auto")

    session.commit()
    session.refresh(event)
    return event.__dict__

@trace_span("service: delete_event")
def delete_event(session: Session, event_id: str):
    event = session.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise NotFound(f"Event with id {event_id} not found")
    session.delete(event)
    session.commit()
    return True

@trace_span("service: search_events")
def search_events(session: Session, filter:EventSearchFilter) -> EventSearchResults:

    query = session.query(Event)

    if filter.Action:
        query = query.filter(Event.Action .like(f'%{filter.Action}%'))
    if filter.UserId:
        query = query.filter(Event.UserId == filter.UserId)
    if filter.TenantId:
        query = query.filter(Event.TenantId == filter.TenantId)
    if filter.EventType:
        query = query.filter(Event.EventType == filter.EventType)
    if filter.FromDate:
        query = query.filter(Event.Timestamp > filter.FromDate)
    if filter.ToDate:
        query = query.filter(Event.Timestamp < filter.ToDate)
    if filter.FromDaysSinceRegistration:
       query = query.filter(Event.DaysSinceRegistration > filter.FromDaysSinceRegistration)
    if filter.ToDaysSinceRegistration:
       query = query.filter(Event.DaysSinceRegistration < filter.ToDaysSinceRegistration)

    if filter.OrderBy == None:
        filter.OrderBy = "CreatedAt"
    else:
        if not hasattr(Event, filter.OrderBy):
            filter.OrderBy = "CreatedAt"
    orderBy = getattr(Event, filter.OrderBy)

    if filter.OrderByDescending:
        query = query.order_by(desc(orderBy))
    else:
        query = query.order_by(asc(orderBy))

    query = query.offset(filter.PageIndex * filter.ItemsPerPage).limit(filter.ItemsPerPage)

    events = query.all()

    items = list(map(lambda x: x.__dict__, events))

    results = EventSearchResults(
        TotalCount=len(events),
        ItemsPerPage=filter.ItemsPerPage,
        PageIndex=filter.PageIndex,
        OrderBy=filter.OrderBy,
        OrderByDescending=filter.OrderByDescending,
        Items=items
    )

    return results

