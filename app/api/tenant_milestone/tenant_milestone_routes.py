from fastapi import APIRouter, Depends, status, HTTPException
from app.api.tenant_milestone.tenant_milestone_handler import (
    create_tenant_milestone_,
    get_tenant_milestone_by_id_,
    update_tenant_milestone_,
    delete_tenant_milestone_,
    search_tenant_milestones_
)
from app.database.database_accessor import get_db_session
from app.domain_types.miscellaneous.response_model import ResponseModel, ResponseStatusTypes
from app.domain_types.schemas.tenant_milestone import TenantMilestoneCreateModel, TenantMilestoneSearchFilter, TenantMilestoneSearchResults, TenantMilestoneUpdateModel, TenantMilestoneResponseModel

###############################################################################

router = APIRouter(
    prefix="/tenant-milestones",
    tags=["tenant-milestones"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ResponseModel[TenantMilestoneResponseModel|None])
async def create_tenant_milestone(model: TenantMilestoneCreateModel, db_session = Depends(get_db_session)):
    return create_tenant_milestone_(model, db_session)

@router.get("/search", status_code=status.HTTP_200_OK, response_model=ResponseModel[TenantMilestoneSearchResults|None])
async def search_tenant_milestone(
        query_params: TenantMilestoneSearchFilter = Depends(),
        db_session = Depends(get_db_session)):
    filter = TenantMilestoneSearchFilter(**query_params.dict())
    return search_tenant_milestones_(filter, db_session)

@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=ResponseModel[TenantMilestoneResponseModel|None])
async def get_tenant_milestone_by_id(id: str, db_session = Depends(get_db_session)):
    return get_tenant_milestone_by_id_(id, db_session)

@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=ResponseModel[TenantMilestoneResponseModel|None])
async def update_tenant_milestone(id: str, model: TenantMilestoneUpdateModel, db_session = Depends(get_db_session)):
    return update_tenant_milestone_(id, model, db_session)

@router.delete("/{id}", status_code=status.HTTP_200_OK, response_model=ResponseModel[bool])
async def delete_tenant_milestone(id: str, db_session = Depends(get_db_session)):
    return delete_tenant_milestone_(id, db_session)
