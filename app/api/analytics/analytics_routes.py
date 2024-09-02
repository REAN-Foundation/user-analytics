from fastapi import APIRouter, Depends, status, HTTPException, BackgroundTasks
from app.api.analytics.analytics_handler import (
    get_analytics_till_date_,
)
from app.database.database_accessor import get_db_session
from app.domain_types.miscellaneous.response_model import ResponseModel, ResponseStatusTypes
from app.domain_types.schemas.user import UserCreateModel, UserMetadataUpdateModel, UserSearchFilter, UserSearchResults, UserResponseModel

###############################################################################

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

@router.get("/date/:date", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool|None])
async def calculate_analytics_till_date(background_tasks: BackgroundTasks):
    background_tasks.add_task(get_analytics_till_date_)
    message = "Standard Analytics processing till the given date has started. Please check the access URL for more details."
    resp = ResponseModel[bool](Message=message, Data=True)
    return resp
