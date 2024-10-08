from datetime import datetime
from typing import Any, List, Optional
from pydantic import UUID4, BaseModel, Field
from app.domain_types.schemas.base_types import BaseSearchFilter, BaseSearchResults

class TenantMilestoneCreateModel(BaseModel):
    TenantId                    : UUID4              = Field(description="Id of the Tenant")
    MilestoneName               : str                = Field(min_length=2, max_length=256, description="Name of the Milestone")
    MilestoneCategory           : str                = Field(min_length=2, max_length=256, description="Category of the Milestone")
    Attributes                  : Optional[Any|None] = Field(default=None, description="Attributes of the Milestone")
    Timestamp                   : datetime           = Field(default=None, description="Timestamp of the Milestone")

TenantMilestoneCreateModel.update_forward_refs()

class TenantMilestoneUpdateModel(BaseModel):
    TenantId                    : Optional[UUID4]    = Field(description="Id of the Tenant")
    MilestoneName               : Optional[str]      = Field(min_length=2, max_length=256, description="Name of the Milestone")
    MilestoneCategory           : Optional[str]      = Field(min_length=2, max_length=256, description="Category of the Milestone")
    Attributes                  : Optional[Any|None] = Field(default=None, description="Attributes of the Milestone")
    Timestamp                   : Optional[datetime] = Field(default=None, description="Timestamp of the Milestone")

TenantMilestoneUpdateModel.update_forward_refs()

class TenantMilestoneSearchFilter(BaseSearchFilter):
    TenantId                       : Optional[UUID4]
    MilestoneName                  : Optional[str]
    MilestoneCategory              : Optional[str]
    Attribute                      : Optional[str]
    FromDate                       : Optional[datetime]
    ToDate                         : Optional[datetime]

TenantMilestoneSearchFilter.update_forward_refs()

class TenantMilestoneResponseModel(BaseModel):
    id                          : UUID4                 = Field(description="Id of the Milestone")
    TenantId                    : UUID4                 = Field(description="Id of the Tenant")
    MilestoneName               : str                   = Field(min_length=2, max_length=256, description="Name of the Milestone")
    MilestoneCategory           : str                   = Field(min_length=2, max_length=256, description="Category of the Milestone")
    Attributes                  : Optional[Any | None]  = Field(default=None, description="Attributes of the Milestone")
    Timestamp                   : datetime              = Field(default=None, description="Timestamp of the Milestone")

TenantMilestoneResponseModel.update_forward_refs()

class TenantMilestoneSearchResults(BaseSearchResults):
    Items: List[TenantMilestoneResponseModel] = []
