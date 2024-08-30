from datetime import datetime
from typing import Any, List, Optional
from pydantic import UUID4, BaseModel, Field
from app.domain_types.enums.types import EventActionType
from app.domain_types.schemas.base_types import BaseSearchFilter, BaseSearchResults

class EventCreateModel(BaseModel):
    UserId          : UUID4              = Field(description="Id of the User")
    TenantId        : UUID4              = Field(description="Tenant Id of the User")
    SessionId       : Optional[UUID4]    = Field(default=None, description="Session Id of the Event")
    ResourceId      : Optional[UUID4]    = Field(default=None, description="Resource Id of the Event")
    ResourceType    : Optional[str|None] = Field(default=None, min_length=2, max_length=256, description="Type of the resource")
    SourceName      : Optional[str]      = Field(default=None, min_length=2, max_length=256, description="Name of the Event")
    SourceVersion   : Optional[str]      = Field(default=None, min_length=2, max_length=256, description="Version of the Event")
    EventName       : str                = Field(min_length=2, max_length=256, description="Name of the Event")
    EventCategory   : str                = Field(min_length=2, max_length=128, description="Type of the Event")
    ActionType      : EventActionType    = Field(min_length=2, max_length=128, description="Type of the Action")
    ActionStatement : str                = Field(min_length=2, max_length=512, description="Action Statement statement of event. Used for history tracking.")
    Timestamp       : datetime           = Field(default=None, description="Timestamp of the Event")
    Attributes      : Optional[Any|None] = Field(default=None, description="Attributes of the Event")

EventCreateModel.update_forward_refs()

class EventUpdateModel(BaseModel):
    pass

class EventSearchFilter(BaseSearchFilter):
    UserId                         : Optional[UUID4]
    TenantId                       : Optional[UUID4]
    ResourceId                     : Optional[UUID4]
    ResourceType                   : Optional[str]
    SessionId                      : Optional[UUID4]
    EventName                      : Optional[str]
    SourceName                     : Optional[str]
    SourceVersion                  : Optional[str]
    EventCategory                  : Optional[str]
    ActionType                     : Optional[EventActionType]
    Attribute                      : Optional[str]
    FromDate                       : Optional[datetime]
    ToDate                         : Optional[datetime]
    FromDaysSinceRegistration      : Optional[int]
    ToDaysSinceRegistration        : Optional[int]
    FromTimeOffsetSinceRegistration: Optional[int]
    ToTimeOffsetSinceRegistration  : Optional[int]

EventSearchFilter.update_forward_refs()

class EventResponseModel(BaseModel):
    id                          : UUID4                 = Field(description="Id of the Event")
    UserId                      : UUID4                 = Field(description="Id of the User")
    TenantId                    : UUID4                 = Field(description="Tenant Id of the User")
    ResourceId                  : Optional[UUID4]       = Field(default=None, description="Resource Id of the Event")
    ResourceType                : Optional[str]         = Field(min_length=2, max_length=256, description="Type of the resource")
    SessionId                   : Optional[UUID4]       = Field(default=None, description="Session Id of the Event")
    EventName                   : str                   = Field(min_length=2, max_length=256, description="Name of the Event")
    SourceName                  : str                   = Field(min_length=2, max_length=256, description="Name of the Event")
    SourceVersion               : Optional[str]         = Field(min_length=2, max_length=256, description="Version of the Event")
    EventCategory               : str                   = Field(min_length=2, max_length=128, description="Type of the Event")
    ActionType                  : EventActionType       = Field(min_length=2, max_length=128, description="Type of the Action")
    ActionStatement             : Optional[str]         = Field(min_length=2, max_length=512, description="Action statement of the Event. Used for history tracking.")
    Timestamp                   : datetime              = Field(default=None, description="Timestamp of the Event")
    Attributes                  : Optional[Any | None]  = Field(default=None, description="Attributes of the Event")
    DaysSinceRegistration       : Optional[int | None]  = Field(default=None, description="Days since registration")
    TimeOffsetSinceRegistration : Optional[int | None]  = Field(default=None, description="Time offset since registration")
    CreatedAt                   : datetime              = Field(default=None, description="Created At timestamp of the Event")
    UpdatedAt                   : datetime              = Field(default=None, description="Updated At timestamp of the Event")

EventResponseModel.model_rebuild()

class EventSearchResults(BaseSearchResults):
    Items: List[EventResponseModel] = []
