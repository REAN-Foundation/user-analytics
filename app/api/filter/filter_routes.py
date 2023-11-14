from fastapi import APIRouter, Depends, status
from app.api.filter.filter_handler import (
    create_filter_,
    get_filter_by_id_,
    update_filter_,
    delete_filter_,
    search_filters_
)
from app.database.database_accessor import get_db_session
from app.domain_types.miscellaneous.response_model import ResponseModel
from app.domain_types.schemas.filter import FilterCreateModel, FilterResponseModel, FilterUpdateModel, FilterSearchFilter, FilterSearchResults

###############################################################################

router = APIRouter(
    prefix="/filters",
    tags=["filters"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ResponseModel[FilterResponseModel|None])
async def create_filter(model: FilterCreateModel, db_session = Depends(get_db_session)):
    return create_filter_(model, db_session)

@router.get("/search", status_code=status.HTTP_200_OK, response_model=ResponseModel[FilterSearchResults|None])
async def search_filters(
        query_params: FilterSearchFilter = Depends(),
        db_session = Depends(get_db_session)):
    filter = FilterSearchFilter(**query_params.dict())
    return search_filters_(filter, db_session)

@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=ResponseModel[FilterResponseModel|None])
async def get_filter_by_id(id: str, db_session = Depends(get_db_session)):
    return get_filter_by_id_(id, db_session)

@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=ResponseModel[FilterResponseModel|None])
async def update_filter(id: str, model: FilterUpdateModel, db_session = Depends(get_db_session)):
    return update_filter_(id, model, db_session)

@router.delete("/{id}", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool])
async def delete_filter(id: str, db_session = Depends(get_db_session)):
    return delete_filter_(id, db_session)

