from fastapi import APIRouter, Depends, status, HTTPException, BackgroundTasks
from app.api.sync.sync_handler import (
    sync_medication_create_events_,
    sync_medication_delete_events_,
    sync_medication_schedule_missed_events_,
    sync_medication_schedule_taken_events_,
    sync_user_login_session_events_,
    sync_users_,
)
from app.database.database_accessor import get_db_session
from app.domain_types.miscellaneous.response_model import ResponseModel, ResponseStatusTypes
from app.domain_types.schemas.user import UserCreateModel, UserMetadataUpdateModel, UserSearchFilter, UserSearchResults, UserResponseModel

###############################################################################

router = APIRouter(
    prefix="/sync",
    tags=["sync"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

@router.post("/users", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_users(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_users_)
    message = "Users synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/logins", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_user_login_session_events(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_user_login_session_events_)
    message = "User login session events synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/medications/create", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_medication_create_events(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_medication_create_events_)
    message = "Medication create events synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/medications/delete", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_medication_delete_events(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_medication_delete_events_)
    message = "Medication delete events synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/medication-schedules/taken", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_medication_schedule_taken_events(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_medication_schedule_taken_events_)
    message = "Medication schedule taken events synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/medication-schedules/missed", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_medication_schedule_missed_events(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_medication_schedule_missed_events_)
    message = "Medication schedule missed events synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp
