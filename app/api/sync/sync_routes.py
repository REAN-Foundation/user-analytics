from typing import Optional
from fastapi import APIRouter, Query, status, BackgroundTasks
from app.api.sync.sync_handler import (
    sync_assessment_events_,
    sync_biometric_events_,
    sync_careplan_events_,
    sync_exercise_events_,
    sync_goal_events_,
    sync_lab_record_events_,
    sync_medication_events_,
    sync_meditation_events_,
    sync_mood_events_,
    sync_nutrition_events_,
    sync_sleep_events_,
    sync_stand_events_,
    sync_step_events_,
    sync_symptom_events_,
    sync_user_account_events_,
    sync_user_login_session_events_,
    sync_user_task_events_,
    sync_users_,
)
from app.common.validators import validate_data_sync_search_filter
from app.domain_types.miscellaneous.response_model import ResponseModel

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

@router.post("/events/user-accounts", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_user_account_events(background_tasks: BackgroundTasks,
                                start_date: Optional[str]  = Query(None, alias="StartDate"),
                                end_date: Optional[str]  = Query(None, alias="EndDate")):
    filters = validate_data_sync_search_filter(start_date, end_date)
    background_tasks.add_task(sync_user_account_events_, filters)
    message = "User account events synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/logins", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_user_login_session_events(background_tasks: BackgroundTasks,
                                    start_date: Optional[str]  = Query(None, alias="StartDate"),
                                    end_date: Optional[str]  = Query(None, alias="EndDate")):
    filters = validate_data_sync_search_filter(start_date, end_date)
    background_tasks.add_task(sync_user_login_session_events_, filters)
    message = "User login session events synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/medications", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_medication_events(background_tasks: BackgroundTasks,
                                start_date: Optional[str]  = Query(None, alias="StartDate"),
                                end_date: Optional[str]  = Query(None, alias="EndDate")):
    filters = validate_data_sync_search_filter(start_date, end_date)    
    background_tasks.add_task(sync_medication_events_, filters)
    message = "Medication events synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/symptoms", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_symptom_events(background_tasks: BackgroundTasks, 
                              start_date: Optional[str]  = Query(None, alias="StartDate"),
                              end_date: Optional[str]  = Query(None, alias="EndDate")):
    
    filters = validate_data_sync_search_filter(start_date, end_date)                       
    background_tasks.add_task(sync_symptom_events_, filters)
    message = "Symptom events synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/lab-records", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_lab_record_events(background_tasks: BackgroundTasks,
                                start_date: Optional[str]  = Query(None, alias="StartDate"),
                                end_date: Optional[str]  = Query(None, alias="EndDate")):
    filters = validate_data_sync_search_filter(start_date, end_date)
    background_tasks.add_task(sync_lab_record_events_, filters)
    message = "Lab Record events synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/biometrics", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_biometric_events(background_tasks: BackgroundTasks,
                            start_date: Optional[str]  = Query(None, alias="StartDate"),
                            end_date: Optional[str]  = Query(None, alias="EndDate")):
    filters = validate_data_sync_search_filter(start_date, end_date)
    background_tasks.add_task(sync_biometric_events_, filters)
    message = "Biometrics events synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/assessments", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_assessment_events(background_tasks: BackgroundTasks,
                            start_date: Optional[str]  = Query(None, alias="StartDate"),
                            end_date: Optional[str]  = Query(None, alias="EndDate")):
    filters = validate_data_sync_search_filter(start_date, end_date)
    background_tasks.add_task(sync_assessment_events_, filters)
    message = "Assessment events synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/careplans", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_careplan_events(background_tasks: BackgroundTasks,
                            start_date: Optional[str]  = Query(None, alias="StartDate"),
                            end_date: Optional[str]  = Query(None, alias="EndDate")):
    filters = validate_data_sync_search_filter(start_date, end_date)
    background_tasks.add_task(sync_careplan_events_, filters)
    message = "Careplan events synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/user-tasks", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_user_task_events(background_tasks: BackgroundTasks,
                            start_date: Optional[str]  = Query(None, alias="StartDate"),
                            end_date: Optional[str]  = Query(None, alias="EndDate")):
    filters = validate_data_sync_search_filter(start_date, end_date)
    background_tasks.add_task(sync_user_task_events_, filters)
    message = "User Task events synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/steps", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_step_events(background_tasks: BackgroundTasks,
                                start_date: Optional[str]  = Query(None, alias="StartDate"),
                                end_date: Optional[str]  = Query(None, alias="EndDate")):
    filters = validate_data_sync_search_filter(start_date, end_date)
    background_tasks.add_task(sync_step_events_, filters)
    message = "Step events synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/sleeps", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_sleep_events(background_tasks: BackgroundTasks,
                                start_date: Optional[str]  = Query(None, alias="StartDate"),
                                end_date: Optional[str]  = Query(None, alias="EndDate")):
    filters = validate_data_sync_search_filter(start_date, end_date)
    background_tasks.add_task(sync_sleep_events_, filters)
    message = "Sleep events synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp


@router.post("/events/nutritions", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_nutrition_events(background_tasks: BackgroundTasks,
                                start_date: Optional[str]  = Query(None, alias="StartDate"),
                                end_date: Optional[str]  = Query(None, alias="EndDate")):
    filters = validate_data_sync_search_filter(start_date, end_date)
    background_tasks.add_task(sync_nutrition_events_, filters)
    message = "Nutrition synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/stands", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_stand_events(background_tasks: BackgroundTasks,
                                start_date: Optional[str]  = Query(None, alias="StartDate"),
                                end_date: Optional[str]  = Query(None, alias="EndDate")):
    filters = validate_data_sync_search_filter(start_date, end_date)
    background_tasks.add_task(sync_stand_events_, filters)
    message = "Stand synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/moods", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_mood_events(background_tasks: BackgroundTasks,
                                start_date: Optional[str]  = Query(None, alias="StartDate"),
                                end_date: Optional[str]  = Query(None, alias="EndDate")):
    filters = validate_data_sync_search_filter(start_date, end_date)
    background_tasks.add_task(sync_mood_events_, filters)
    message = "Mood synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/meditations", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_meditation_events(background_tasks: BackgroundTasks,
                                start_date: Optional[str]  = Query(None, alias="StartDate"),
                                end_date: Optional[str]  = Query(None, alias="EndDate")):
    filters = validate_data_sync_search_filter(start_date, end_date)
    background_tasks.add_task(sync_meditation_events_, filters)
    message = "Meditation synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/goals", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_goal_events(background_tasks: BackgroundTasks,
                                start_date: Optional[str]  = Query(None, alias="StartDate"),
                                end_date: Optional[str]  = Query(None, alias="EndDate")):
    filters = validate_data_sync_search_filter(start_date, end_date)
    background_tasks.add_task(sync_goal_events_, filters)
    message = "Goal synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/exercises", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_exercise_events(background_tasks: BackgroundTasks,
                                start_date: Optional[str]  = Query(None, alias="StartDate"),
                                end_date: Optional[str]  = Query(None, alias="EndDate")):
    filters = validate_data_sync_search_filter(start_date, end_date)
    background_tasks.add_task(sync_exercise_events_, filters)
    message = "Exercise synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp
