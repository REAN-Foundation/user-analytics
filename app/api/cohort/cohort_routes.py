from fastapi import APIRouter, Depends, status, Query, Body
from app.common.utils import print_colorized_json, validate_uuid4
from app.database.database_accessor import get_db_session
from app.api.cohort.cohort_handler import (
    create_cohort_,
    get_cohort_by_id_,
    update_cohort_,
    delete_cohort_,
    search_cohortes_
)
from app.domain_types.schemas.cohort import CohortCreateModel, CohortUpdateModel, CohortResponseModel, CohortSearchResults, CohortSearchFilter
from app.domain_types.miscellaneous.response_model import ResponseModel, ResponseStatusTypes

router = APIRouter(
    prefix="/cohortes",
    tags=["cohortes"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ResponseModel[CohortResponseModel] | None)
async def create_cohort(model: CohortCreateModel, db_session=Depends(get_db_session)):
    return create_cohort_(model, db_session)

@router.get("/search", status_code=status.HTTP_200_OK, response_model=ResponseModel[CohortSearchResults|None])
async def search_cohort(
        query_params: CohortSearchFilter = Depends(),
        db_session = Depends(get_db_session)):
    filter = CohortSearchFilter(**query_params.dict())
    return search_cohortes_(filter, db_session)

@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=ResponseModel[CohortResponseModel] | None)
async def get_cohort_by_id(id: str, db_session=Depends(get_db_session)):
    return get_cohort_by_id_(id, db_session)

@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=CohortResponseModel | None)
async def update_cohort(id: str, model: CohortUpdateModel, db_session=Depends(get_db_session)):
    return update_cohort_(id, model, db_session)

@router.delete("/{id}", status_code=status.HTTP_200_OK, response_model=ResponseModel[CohortResponseModel] | None)
async def delete_cohort(id: str, db_session=Depends(get_db_session)):
    return delete_cohort(id, db_session)

