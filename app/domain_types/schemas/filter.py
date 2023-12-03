from datetime import datetime
from typing import Any, List, Optional
from pydantic import UUID4, BaseModel, Field
from app.domain_types.enums.types import AnalysisType, Duration, Frequency
from app.domain_types.schemas.base_types import BaseSearchFilter, BaseSearchResults

###############################################################################

class FilterCreateModel(BaseModel):
    Name         : str           = Field(..., min_length=2, max_length=256)
    Description  : str           = Field(..., min_length=2, max_length=1024)
    OwnerId      : UUID4         = Field(default=None)
    UserId       : UUID4         = Field(default=None)
    TenantId     : UUID4         = Field(default=None)
    AnalysisType : Optional[AnalysisType]
    Frequency    : Optional[Frequency]
    Duration     : Optional[Duration]
    Filters      : Optional[Any] = Field(default=None)

FilterCreateModel.update_forward_refs()

class FilterUpdateModel(BaseModel):
    Name        : Optional[str]            = Field(..., min_length=2, max_length=256)
    Description : Optional[str]            = Field(..., min_length=2, max_length=1024)
    UserId      : Optional[UUID4]          = Field(default=None)
    TenantId    : Optional[UUID4]          = Field(default=None)
    AnalysisType: Optional[AnalysisType]
    Source      : Optional[Frequency]
    Duration    : Optional[Duration]
    Filters     : Optional[Any] = Field(default=None)

FilterUpdateModel.update_forward_refs()

class FilterSearchFilter(BaseSearchFilter):
    Name         : Optional[str]          = Field(description="Search filter by name")
    Description  : Optional[str]          = Field(description="Search filter by description")
    UserId       : Optional[UUID4]        = Field(description="Search filter by user id")
    TenantId     : Optional[UUID4]        = Field(description="Search filter by tenant id")
    OwnerId      : Optional[UUID4]        = Field(description="Search filter by owner id")
    AnalysisType : Optional[AnalysisType]
    Frequency    : Optional[Frequency]
    Duration     : Optional[Duration]

FilterSearchFilter.update_forward_refs()

class FilterResponseModel(BaseModel):
    id           : UUID4         = Field(description="Id of the filter")
    Name         : str           = Field(description="Name of the filter")
    Description  : str           = Field(description="Description of filter")
    OwnerId      : UUID4         = Field(description="Id of the owner", default=None)
    UserId       : UUID4         = Field(description="Id of the user", default=None)
    TenantId     : UUID4         = Field(description="Id of the tenant", default=None)
    AnalysisType : AnalysisType  #= None #AnalysisType.TotalUsers
    Frequency    : Frequency     #= None #Frequency.PerDay
    Duration     : Duration      #= None #Duration.LastWeek
    Filters      : Optional[Any] = Field(description="Filters key value pairs", default=None)
    CreatedAt    : datetime      = Field(description="Created at")
    UpdatedAt    : datetime      = Field(description="Updated at")

FilterResponseModel.update_forward_refs()

class FilterSearchResults(BaseSearchResults):
    Items : List[FilterResponseModel] = Field(description="List of filters")

