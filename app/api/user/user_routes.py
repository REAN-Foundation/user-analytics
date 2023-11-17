from fastapi import APIRouter, Depends, status, HTTPException
from app.api.user.user_handler import (
    create_user_,
    get_user_by_id_,
    update_user_,
    delete_user_,
    search_users_
)
from app.database.database_accessor import get_db_session
from app.domain_types.miscellaneous.exceptions import handle_failure
from app.domain_types.miscellaneous.response_model import ResponseModel, ResponseStatusTypes
from app.domain_types.schemas.user import UserCreateModel, UserSearchFilter, UserSearchResults, UserUpdateModel, UserResponseModel

###############################################################################

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ResponseModel[UserResponseModel|None])
async def create_user(model: UserCreateModel, db_session = Depends(get_db_session)):
    try:
        return create_user_(model, db_session)
    except Exception as e:
        handle_failure(e)

@router.get("/search", status_code=status.HTTP_200_OK, response_model=ResponseModel[UserSearchResults|None])
async def search_user(
        query_params: UserSearchFilter = Depends(),
        db_session = Depends(get_db_session)):
    try:
        filter = UserSearchFilter(**query_params.dict())
        return search_users_(filter, db_session)
    except Exception as e:
        handle_failure(e)

@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=ResponseModel[UserResponseModel|None])
async def get_user_by_id(id: str, db_session = Depends(get_db_session)):
    try:
        return get_user_by_id_(id, db_session)
    except Exception as e:
        handle_failure(e)

@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=ResponseModel[UserResponseModel|None])
async def update_user(id: str, model: UserUpdateModel, db_session = Depends(get_db_session)):
    try:
        return update_user_(id, model, db_session)
    except Exception as e:
        handle_failure(e)

@router.delete("/{id}", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool])
async def delete_user(id: str, db_session = Depends(get_db_session)):
    try:
        return delete_user_(id, db_session)
    except Exception as e:
        handle_failure(e)
