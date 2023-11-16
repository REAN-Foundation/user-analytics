from datetime import datetime
from typing import List, Optional
from pydantic import UUID4, BaseModel, Field
from app.domain_types.schemas.base_search_types import BaseSearchFilter, BaseSearchResults

class CohortCreateModel(BaseModel):
    Name        : str            = Field(min_length=2, max_length=256)
    Description : str            = Field(min_length=2, max_length=1024)
    TenantId    : UUID4          = Field(default=None)
    Attributes  : Optional[dict] = Field(default=None)

class CohortUpdateModel(BaseModel):
    Name        : Optional[str]  = Field(min_length=2, max_length=256)
    Description : Optional[str]  = Field(min_length=2, max_length=1024)
    Attributes  : Optional[dict] = Field(default=None)

class CohortSearchFilter(BaseSearchFilter):
    TenantId : Optional[str] = Field(description="Search by the tenant")
    Name     : Optional[str] = Field(description="Search by the name of the Cohort")
    Attribute: Optional[str] = Field(description="Search by the attribute of the Cohort")
    OwnerId  : Optional[str] = Field(description="Search by the owner id of the Cohort")

class CohortResponseModel(BaseModel):
    id          : UUID4
    Name        : str
    Description : str
    TenantId    : UUID4
    OwnerId     : UUID4
    Attributes  : Optional[dict]
    Users       : Optional[List[dict]]
    CreatedAt   : datetime
    UpdatedAt   : datetime

class CohortSearchResults(BaseSearchResults):
    Items: List[CohortResponseModel] = []
