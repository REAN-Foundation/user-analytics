from fastapi import APIRouter, Depends, status
from app.api.event.event_handler import (
    create_event_,
    get_event_by_id_,
    update_event_,
    delete_event_,
    search_events_
)
from app.database.database_accessor import get_db_session
from app.domain_types.miscellaneous.response_model import ResponseModel
from app.domain_types.schemas.event import EventCreateModel, EventResponseModel, EventUpdateModel, EventSearchFilter, EventSearchResults

###############################################################################

router = APIRouter(
    prefix="/events",
    tags=["events"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ResponseModel[EventResponseModel|None])
async def create_event(model: EventCreateModel, db_session = Depends(get_db_session)):
    return create_event_(model, db_session)

@router.get("/search", status_code=status.HTTP_200_OK, response_model=ResponseModel[EventSearchResults|None])
async def search_event(
        query_params: EventSearchFilter = Depends(),
        db_session = Depends(get_db_session)):
    filter = EventSearchFilter(**query_params.dict())
    return search_events_(filter, db_session)

@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=ResponseModel[EventResponseModel|None])
async def get_event_by_id(id: str, db_session = Depends(get_db_session)):
    return get_event_by_id_(id, db_session)

@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=ResponseModel[EventResponseModel|None])
async def update_event(id: str, model: EventUpdateModel, db_session = Depends(get_db_session)):
    return update_event_(id, model, db_session)

@router.delete("/{id}", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool])
async def delete_event(id: str, db_session = Depends(get_db_session)):
    return delete_event_(id, db_session)

@router.get("/search", status_code=status.HTTP_200_OK, response_model=ResponseModel[EventSearchResults|None])
async def search_event(
        query_params: EventSearchFilter = Depends(),
        db_session = Depends(get_db_session)):
    filter = EventSearchFilter(**query_params.dict())
    return search_events_(filter, db_session)
