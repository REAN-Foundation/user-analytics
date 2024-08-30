from fastapi import APIRouter, Depends, status, HTTPException
from app.api.user_milestone.user_milestone_handler import (
    create_user_milestone_,
    get_user_milestone_by_id_,
    update_user_milestone_,
    delete_user_milestone_,
    search_user_milestones_
)
from app.database.database_accessor import get_db_session
from app.domain_types.miscellaneous.response_model import ResponseModel, ResponseStatusTypes
from app.domain_types.schemas.user_milestone import UserMilestoneCreateModel, UserMilestoneSearchFilter, UserMilestoneSearchResults, UserMilestoneUpdateModel, UserMilestoneResponseModel

###############################################################################

router = APIRouter(
    prefix="/user-milestones",
    tags=["user-milestones"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ResponseModel[UserMilestoneResponseModel|None])
async def create_user_milestone(model: UserMilestoneCreateModel, db_session = Depends(get_db_session)):
    return create_user_milestone_(model, db_session)

@router.get("/search", status_code=status.HTTP_200_OK, response_model=ResponseModel[UserMilestoneSearchResults|None])
async def search_user_milestone(
        query_params: UserMilestoneSearchFilter = Depends(),
        db_session = Depends(get_db_session)):
    filter = UserMilestoneSearchFilter(**query_params.dict())
    return search_user_milestones_(filter, db_session)

@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=ResponseModel[UserMilestoneResponseModel|None])
async def get_user_milestone_by_id(id: str, db_session = Depends(get_db_session)):
    return get_user_milestone_by_id_(id, db_session)

@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=ResponseModel[UserMilestoneResponseModel|None])
async def update_user_milestone(id: str, model: UserMilestoneUpdateModel, db_session = Depends(get_db_session)):
    return update_user_milestone_(id, model, db_session)

@router.delete("/{id}", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool])
async def delete_user_milestone(id: str, db_session = Depends(get_db_session)):
    return delete_user_milestone_(id, db_session)
