from datetime import datetime
from typing import Any, List, Optional
from pydantic import UUID4, BaseModel, Field
from app.domain_types.enums.types import EventActionType, MilestoneType
from app.domain_types.schemas.base_types import BaseSearchFilter, BaseSearchResults

class MilestoneCreateModel(BaseModel):
    UserId          : UUID4              = Field(description="Id of the User")
    TenantId        : UUID4              = Field(description="Tenant Id of the User")
    # ResourceId      : Optional[UUID4]    = Field(default=None, description="Resource Id of the Event")
    # ResourceType    : Optional[str]      = Field(min_length=2, max_length=256, description="Type of the resource")
    # SessionId       : Optional[UUID4]    = Field(default=None, description="Session Id of the Event")
    # SourceName      : str                = Field(min_length=2, max_length=256, description="Name of the Event")
    # SourceVersion   : Optional[str]      = Field(min_length=2, max_length=256, description="Version of the Event")
    MilestoneName     : MilestoneType    = Field(min_length=2, max_length=256, description="Name of the Milestone")
    MilestoneCategory : str              = Field(min_length=2, max_length=128, description="Type of the Milestone")
    # ActionType      : EventActionType    = Field(min_length=2, max_length=128, description="Type of the Action")
    # ActionStatement : str                = Field(min_length=2, max_length=512, description="Action Statement statement of event. Used for history tracking.")
    Timestamp       : datetime           = Field(default=None, description="Timestamp of the Milestone")
    Attributes      : Optional[Any|None] = Field(default=None, description="Attributes of the Milestone")

MilestoneCreateModel.update_forward_refs()
