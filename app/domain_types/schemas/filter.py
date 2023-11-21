from datetime import datetime
from typing import Any, List, Optional
from pydantic import UUID4, BaseModel, Field
from app.domain_types.enums.types import AnalysisType, Duration, Frequency
from app.domain_types.schemas.base_search_types import BaseSearchFilter, BaseSearchResults

###############################################################################

class FilterCreateModel(BaseModel):
    Name         : str           = Field(..., min_length=2, max_length=256)
    Description  : str           = Field(..., min_length=2, max_length=1024)
    OwnerId      : UUID4         = Field(default=None)
    UserId       : UUID4         = Field(default=None)
    TenantId     : UUID4         = Field(default=None)
    AnalysisType : AnalysisType  = AnalysisType.active_users
    Frequency    : Frequency     = Frequency.per_day
    Duration     : Duration      = Duration.last_7_days
    Filters      : Optional[Any] = Field(default=None)

class FilterUpdateModel(BaseModel):
    Name        : Optional[str]            = Field(..., min_length=2, max_length=256)
    Description : Optional[str]            = Field(..., min_length=2, max_length=1024)
    UserId      : Optional[UUID4]          = Field(default=None)
    TenantId    : Optional[UUID4]          = Field(default=None)
    AnalysisType: Optional[AnalysisType]
    Source      : Optional[Frequency]
    Duration    : Optional[Duration]
    Filters     : Optional[Any] = Field(default=None)

class FilterSearchFilter(BaseSearchFilter):
    Name         : Optional[str]          = Field(description="Search filter by name")
    Description  : Optional[str]          = Field(description="Search filter by description")
    UserId       : Optional[UUID4]        = Field(description="Search filter by user id")
    TenantId     : Optional[UUID4]        = Field(description="Search filter by tenant id")
    OwnerId      : Optional[UUID4]        = Field(description="Search filter by owner id")
    AnalysisType : Optional[AnalysisType]
    Frequency    : Optional[Frequency]
    Duration     : Optional[Duration]

class FilterResponseModel(BaseModel):
    id           : UUID4         = Field(description="Id of the filter")
    Name         : str           = Field(description="Name of the filter")
    Description  : str           = Field(description="Description of filter")
    OwnerId      : UUID4         = Field(description="Id of the owner", default=None)
    UserId       : UUID4         = Field(description="Id of the user", default=None)
    TenantId     : UUID4         = Field(description="Id of the tenant", default=None)
    AnalysisType : AnalysisType  = AnalysisType.active_users
    Frequency    : Frequency     = Frequency.per_day
    Duration     : Duration      = Duration.last_7_days
    Filters      : Optional[Any] = Field(description="Filters key value pairs", default=None)
    CreatedAt    : datetime      = Field(description="Created at")
    UpdatedAt    : datetime      = Field(description="Updated at")

class FilterSearchResults(BaseSearchResults):
    Items : List[FilterResponseModel] = Field(description="List of filters")
