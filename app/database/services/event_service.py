import datetime as dt
import json
import asyncio
from app.database.models.event import Event
from app.database.models.user import User
from app.domain_types.miscellaneous.exceptions import NotFound
from app.domain_types.schemas.event import EventCreateModel, EventResponseModel, EventUpdateModel, EventSearchFilter, EventSearchResults
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import Engine, desc, asc
from app.modules.data_sync.data_synchronizer import DataSynchronizer
from app.telemetry.tracing import trace_span
from datetime import timezone
from app.database.database_accessor import engine

###############################################################################
queue_create_event = asyncio.Queue()
###############################################################################

@trace_span("service: create_event")
async def create_event(model: EventCreateModel):
    asyncio.create_task(worker_create_event(queue_create_event, engine))
    await queue_create_event.put(model)
    return True

async def worker_create_event(create_event_queue: asyncio.Queue, engine: Engine):
    session_ = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)()
    while True:
        model = await create_event_queue.get()
        if model is None:
            break
        add_event_to_db(session_, model)

def add_event_to_db(session_, model):
    try:
        user = DataSynchronizer.get_user(model.UserId)
        if user is None:
            raise NotFound(f"User with id {model.UserId} not found")

        if model.TenantId is not None:
            tenant = DataSynchronizer.get_tenant(model.TenantId)
            if tenant is None:
                raise NotFound(f"Tenant with id {model.TenantId} not found")

        registration_date = user['RegistrationDate'].replace(tzinfo=timezone.utc)

        model_dict = model.dict()
        db_model = Event(**model_dict)
        db_model.Attributes = json.dumps(model.Attributes)
        db_model.UpdatedAt = dt.datetime.now()
        db_model.DaysSinceRegistration = (model.Timestamp - registration_date).days
        db_model.TimeOffsetSinceRegistration = (model.Timestamp - registration_date).total_seconds()
        db_model.Attributes = json.dumps(model.Attributes)

        session_.add(db_model)
        session_.commit()
        temp = session_.refresh(db_model)
        event = db_model
        event.Attributes = json.loads(event.Attributes)
    except Exception as e:
        session_.rollback()
        session_.close()
        raise e
    finally:
        session_.close()

@trace_span("service: get_event_by_id")
def get_event_by_id(session: Session, event_id: str) -> EventResponseModel:
    event = session.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise NotFound(f"Event with id {event_id} not found")
    event.Attributes = json.loads(event.Attributes)
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

    event.Attributes = json.loads(event.Attributes)
    return event.__dict__

@trace_span("service: delete_event")
def delete_event(session: Session, event_id: str) -> bool:
    event = session.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise NotFound(f"Event with id {event_id} not found")
    session.delete(event)
    session.commit()
    return True

@trace_span("service: search_events")
def search_events(session: Session, filter:EventSearchFilter) -> EventSearchResults:

    query = session.query(Event)

    if filter.ActionType:
        query = query.filter(Event.ActionType.like(f'%{filter.ActionType}%'))
    if filter.UserId:
        query = query.filter(Event.UserId == filter.UserId)
    if filter.TenantId:
        query = query.filter(Event.TenantId == filter.TenantId)
    if filter.ResourceId:
        query = query.filter(Event.ResourceId == filter.ResourceId)
    if filter.ResourceType:
        query = query.filter(Event.ResourceType.like(f'%{filter.ResourceType}%'))
    if filter.EventCategory:
        query = query.filter(Event.EventCategory == filter.EventCategory)
    if filter.EventName:
        query = query.filter(Event.EventName.like(f'%{filter.EventName}%'))
    if filter.SourceName:
        query = query.filter(Event.SourceName.like(f'%{filter.SourceName}%'))
    if filter.SourceVersion:
        query = query.filter(Event.SourceVersion.like(f'%{filter.SourceVersion}%'))
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
    for item in items:
        item["Attributes"] = json.loads(item["Attributes"])

    results = EventSearchResults(
        TotalCount=len(events),
        ItemsPerPage=filter.ItemsPerPage,
        PageIndex=filter.PageIndex,
        OrderBy=filter.OrderBy,
        OrderByDescending=filter.OrderByDescending,
        Items=items
    )

    return results

