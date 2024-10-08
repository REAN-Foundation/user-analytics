from datetime import datetime
from typing import Any, List, Optional
from pydantic import UUID4, BaseModel, Field
from app.domain_types.schemas.base_types import BaseSearchFilter, BaseSearchResults

class UserMilestoneCreateModel(BaseModel):
    UserId                      : UUID4              = Field(description="Id of the User")
    MilestoneName               : str                = Field(min_length=2, max_length=256, description="Name of the Milestone")
    MilestoneCategory           : str                = Field(min_length=2, max_length=256, description="Category of the Milestone")
    Attributes                  : Optional[Any|None] = Field(default=None, description="Attributes of the Milestone")
    Timestamp                   : datetime           = Field(default=None, description="Timestamp of the Milestone")
    DaysSinceRegistration       : int                = Field(description="Days since registration")
    TimeOffsetSinceRegistration : int                = Field(description="Time offset since registration")

UserMilestoneCreateModel.update_forward_refs()

class UserMilestoneUpdateModel(BaseModel):
    UserId                      : Optional[UUID4]    = Field(description="Id of the User")
    MilestoneName               : Optional[str]      = Field(min_length=2, max_length=256, description="Name of the Milestone")
    MilestoneCategory           : Optional[str]      = Field(min_length=2, max_length=256, description="Category of the Milestone")
    Attributes                  : Optional[Any|None] = Field(default=None, description="Attributes of the Milestone")
    Timestamp                   : Optional[datetime] = Field(default=None, description="Timestamp of the Milestone")
    DaysSinceRegistration       : Optional[int]      = Field(default=None, description="Days since registration")
    TimeOffsetSinceRegistration : Optional[int]      = Field(default=None, description="Time offset since registration")

UserMilestoneUpdateModel.update_forward_refs()

class UserMilestoneSearchFilter(BaseSearchFilter):
    UserId                         : Optional[UUID4]
    MilestoneName                  : Optional[str]
    MilestoneCategory              : Optional[str]
    Attribute                      : Optional[str]
    FromDate                       : Optional[datetime]
    ToDate                         : Optional[datetime]
    FromDaysSinceRegistration      : Optional[int]
    ToDaysSinceRegistration        : Optional[int]
    FromTimeOffsetSinceRegistration: Optional[int]
    ToTimeOffsetSinceRegistration  : Optional[int]

UserMilestoneSearchFilter.update_forward_refs()

class UserMilestoneResponseModel(BaseModel):
    id                          : UUID4                 = Field(description="Id of the Milestone")
    UserId                      : UUID4                 = Field(description="Id of the User")
    MilestoneName               : str                   = Field(min_length=2, max_length=256, description="Name of the Milestone")
    MilestoneCategory           : str                   = Field(min_length=2, max_length=256, description="Category of the Milestone")
    Attributes                  : Optional[Any | None]  = Field(default=None, description="Attributes of the Milestone")
    Timestamp                   : datetime              = Field(default=None, description="Timestamp of the Milestone")
    DaysSinceRegistration       : Optional[int | None]  = Field(default=None, description="Days since registration")
    TimeOffsetSinceRegistration : Optional[int | None]  = Field(default=None, description="Time offset since registration")

class UserMilestoneSearchResults(BaseSearchResults):
    Items: List[UserMilestoneResponseModel] = []

