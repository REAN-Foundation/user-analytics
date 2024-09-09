from fastapi import APIRouter, Depends, status, HTTPException, BackgroundTasks
from app.api.sync.sync_handler import (
    sync_assessment_create_events_,
    sync_blood_glucose_create_events_,
    sync_blood_glucose_delete_events_,
    sync_blood_pressure_create_events_,
    sync_blood_pressure_delete_events_,
    sync_body_height_create_events_,
    sync_body_height_delete_events_,
    sync_body_temperature_create_events_,
    sync_body_temperature_delete_events_,
    sync_body_weight_create_events_,
    sync_body_weight_delete_events_,
    sync_cholesterol_create_events_,
    sync_cholesterol_delete_events_,
    sync_lab_record_create_events_,
    sync_lab_record_delete_events_,
    sync_medication_create_events_,
    sync_medication_delete_events_,
    sync_medication_schedule_missed_events_,
    sync_medication_schedule_taken_events_,
    sync_oxygen_saturation_create_events_,
    sync_oxygen_saturation_delete_events_,
    sync_pulse_create_events_,
    sync_pulse_delete_events_,
    sync_symptom_create_events_,
    sync_symptom_delete_events_,
    sync_symptom_update_events_,
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

@router.post("/events/symptoms/create", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_symptom_create_events(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_symptom_create_events_)
    message = "Symptom create events synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/symptoms/update", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_symptom_update_events(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_symptom_update_events_)
    message = "Symptom update events synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/symptoms/delete", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_symptom_delete_events(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_symptom_delete_events_)
    message = "Symptom delete events synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/lab-records/create", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_lab_record_create_events(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_lab_record_create_events_)
    message = "Lab Record create events synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/lab-records/delete", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_lab_record_delete_events(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_lab_record_delete_events_)
    message = "Lab Record delete events synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/biometrics/pulse/create", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_pulse_create_events(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_pulse_create_events_)
    message = "Biometrics-Pulse create events synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/biometrics/pulse/delete", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_pulse_delete_events(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_pulse_delete_events_)
    message = "Biometrics-Pulse delete events synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/biometrics/body-weight/create", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_body_weight_create_events(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_body_weight_create_events_)
    message = "Biometrics-Body Weight create events synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/biometrics/body-weight/delete", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_body_weight_delete_events(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_body_weight_delete_events_)
    message = "Biometrics-Body Weight delete events synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/biometrics/body-temperature/create", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_body_temperature_create_events(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_body_temperature_create_events_)
    message = "Biometrics-Body Temperature create events synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/biometrics/body-temperature/delete", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_body_temperature_delete_events(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_body_temperature_delete_events_)
    message = "Biometrics-Body Temperature delete events synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/biometrics/body-height/create", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_body_height_create_events(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_body_height_create_events_)
    message = "Biometrics-Body Height create events synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/biometrics/body-height/delete", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_body_height_delete_events(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_body_height_delete_events_)
    message = "Biometrics-Body Height delete events synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/biometrics/blood-pressure/create", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_blood_pressure_create_events(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_blood_pressure_create_events_)
    message = "Biometrics-Blood Pressure create events synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/biometrics/blood-pressure/delete", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_blood_pressure_delete_events(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_blood_pressure_delete_events_)
    message = "Biometrics-Blood Pressure delete events synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/biometrics/oxygen-saturation/create", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_oxygen_saturation_create_events(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_oxygen_saturation_create_events_)
    message = "Biometrics-Blood Oxygen Saturation create events synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/biometrics/oxygen-saturation/delete", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_oxygen_saturation_delete_events(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_oxygen_saturation_delete_events_)
    message = "Biometrics-Blood Oxygen Saturation delete events synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/biometrics/blood-glucose/create", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_blood_glucose_create_events(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_blood_glucose_create_events_)
    message = "Biometrics-Blood Glucose create events synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/biometrics/blood-glucose/delete", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_blood_glucose_delete_events(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_blood_glucose_delete_events_)
    message = "Biometrics-Blood Glucose delete events synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/biometrics/cholesterol/create", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_cholesterol_create_events(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_cholesterol_create_events_)
    message = "Biometrics-Blood Cholesterol create events synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

@router.post("/events/biometrics/cholesterol/delete", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def sync_cholesterol_delete_events(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_cholesterol_delete_events_)
    message = "Biometrics-Blood Cholesterol delete events synchronization has started."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp

