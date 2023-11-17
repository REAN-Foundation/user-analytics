from datetime import datetime
from typing import List, Optional
from pydantic import UUID4, BaseModel, Field
from app.domain_types.schemas.base_search_types import BaseSearchFilter, BaseSearchResults

class FilterCreateModel(BaseModel):
    Name        : str            = Field(..., min_length=2, max_length=256)
    Description : str            = Field(..., min_length=2, max_length=1024)
    OwnerId     : UUID4          = Field(default=None)
    UserId      : UUID4          = Field(default=None)
    TenantId    : UUID4          = Field(default=None)
    Filters     : Optional[dict] = Field(default=None)

class FilterUpdateModel(BaseModel):
    Name               : Optional[str]           = Field(..., min_length=2, max_length=256)
    Description        : Optional[str]           = Field(..., min_length=2, max_length=1024)
    UserId             : Optional[UUID4]         = Field(default=None)
    TenantId           : Optional[UUID4]         = Field(default=None)
    Filters            : Optional[dict]          = Field(default=None)

class FilterSearchFilter(BaseSearchFilter):
    Name               : Optional[str]           = Field(description="Search filter by name")
    UserId             : Optional[UUID4]         = Field(description="Search filter by user id")
    TenantId           : Optional[UUID4]         = Field(description="Search filter by tenant id")
    OwnerId            : Optional[UUID4]         = Field(description="Search filter by owner id")

class FilterResponseModel(BaseModel):
    id          : UUID4          = Field(description="Id of the filter")
    Name        : UUID4          = Field(description="Id of the filter")
    Description : str            = Field(description="Description of filter")
    OwnerId     : UUID4          = Field(default=None)
    UserId      : UUID4          = Field(default=None)
    TenantId    : UUID4          = Field(default=None)
    Filters     : Optional[dict] = Field(default=None)
    CreatedAt   : datetime       = Field(description="Created at")
    UpdatedAt   : datetime       = Field(description="Updated at")

class FilterSearchResults(BaseSearchResults):
    Items : List[FilterResponseModel] = Field(description="List of filters")
