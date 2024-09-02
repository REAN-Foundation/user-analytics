from datetime import datetime
from typing import List, Optional
from pydantic import UUID4, BaseModel, Field
from app.domain_types.schemas.base_types import BaseSearchFilter, BaseSearchResults

class UserCreateModel(BaseModel):
    id                : UUID4                     = Field(description="Id of the User")
    TenantId          : UUID4                     = Field(description="Tenant Id of the User")
    RoleId            : Optional[int | None]      = Field(default=None, description="Role Id of the User")
    OnboardingSource  : Optional[str | None]      = Field(default=None, min_length=2, max_length=128, description="Source from where user came to the system")
    TimezoneOffsetMin : Optional[int | None]      = Field(default=None, description="Timezone offset of the User")
    RegistrationDate  : Optional[datetime | None] = Field(default=None, description="Registration date of the User")

class UserMetadataUpdateModel(BaseModel):
    BirthDate         : Optional[datetime | None] = Field(default=None, description="Birth date of the User")
    Gender            : str                       = Field(description="Gender of the User")
    LocationLongitude : Optional[float | None]    = Field(default=None, description="Longitude of the User")
    LocationLatitude  : Optional[float | None]    = Field(default=None, description="Latitude of the User")
    Role              : Optional[str | None]      = Field(default=None, min_length=2, max_length=128, description="Role of the User")
    Attributes        : Optional[dict | None]     = Field(default=None, description="Custom attributes of the User")
    Ethnicity         : Optional[str | None]      = Field(default=None, min_length=2, max_length=128, description="Ethnicity of the User")
    Race              : Optional[str | None]      = Field(default=None, min_length=2, max_length=128, description="Race of the User")
    HealthSystem      : Optional[str | None]      = Field(default=None, min_length=2, max_length=128, description="Health system of the User")
    Hospital          : Optional[str | None]      = Field(default=None, min_length=2, max_length=128, description="Hospital of the User")
    IsCareGiver       : Optional[bool | None]     = Field(default=None, description="Is the User a Care Giver")
    MajorDiagnosis    : Optional[str | None]      = Field(default=None, min_length=2, max_length=128, description="Major diagnosis of the User")
    Smoker            : Optional[bool | None]     = Field(default=None, description="Is the User a Smoker")
    Alcoholic         : Optional[bool | None]     = Field(default=None, description="Is the User an Alcoholic")

class UserSearchFilter(BaseSearchFilter):
    TenantId         : Optional[UUID4] = Field(description="Search by Tenant Id")
    RoleId           : Optional[int]   = Field(description="Search by Role Id")
    LastActiveBefore : Optional[datetime] = Field(description="Search by the date before which the User was last active")
    LastActiveAfter  : Optional[datetime] = Field(description="Search by the date after which the User was last active")
    RegisteredBefore : Optional[datetime] = Field(description="Search Users registered before the given date")
    RegisteredAfter  : Optional[datetime] = Field(description="Search Users registered after the given date")

class UserResponseModel(BaseModel):
    id                : UUID4                     = Field(description="Id of the User")
    TenantId          : UUID4                     = Field(description="Tenant Id of the User")
    RoleId            : Optional[int | None]      = Field(default=None, description="Role Id of the User")
    TimezoneOffsetMin : Optional[int | None]      = Field(default=None, description="Timezone offset of the User")
    RegistrationDate  : Optional[datetime | None] = Field(default=None, description="Registration date of the User")
    Metadata          : Optional[UserMetadataUpdateModel | None] = Field(default=None, description="Metadata of the User")
    UpdatedAt         : datetime                  = Field(description="Updated at")
    DeletedAt         : Optional[datetime | None] = Field(default=None, description="Deleted at")

class UserSearchResults(BaseSearchResults):
    Items : List[UserResponseModel] = Field(description="List of Users")
