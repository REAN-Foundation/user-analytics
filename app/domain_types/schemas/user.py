from datetime import datetime
from typing import List, Optional
from pydantic import UUID4, BaseModel, Field
from app.domain_types.schemas.base_types import BaseSearchFilter, BaseSearchResults

class UserCreateModel(BaseModel):
    id                : UUID4                     = Field(description="Id of the User")
    TenantId          : UUID4                     = Field(description="Tenant Id of the User")
    BirthDate         : Optional[datetime | None] = Field(default=None, description="Birth date of the User")
    Gender            : str                       = Field(description="Gender of the User")
    LocationLongitude : Optional[float | None]    = Field(default=None, description="Longitude of the User")
    LocationLatitude  : Optional[float | None]    = Field(default=None, description="Latitude of the User")
    LastActive        : Optional[datetime | None] = Field(default=None, description="Last active time of the User")
    OnboardingSource  : Optional[str | None]      = Field(default=None, min_length=2, max_length=128, description="Source from where user came to the system")
    Role              : Optional[str | None]      = Field(default=None, min_length=2, max_length=128, description="Role of the User")
    Attributes        : Optional[dict | None]     = Field(default=None, description="Custom attributes of the User")
    TimezoneOffsetMin : Optional[int | None]      = Field(default=None, description="Timezone offset of the User")
    RegistrationDate  : Optional[datetime | None] = Field(default=None, description="Registration date of the User")


class UserUpdateModel(BaseModel):
    BirthDate         : Optional[datetime | None] = Field(default=None, description="Birth date of the User")
    Gender            : Optional[str | None]      = Field(description="Gender of the User")
    LocationLongitude : Optional[float | None]    = Field(default=None, description="Longitude of the User")
    LocationLatitude  : Optional[float | None]    = Field(default=None, description="Latitude of the User")
    LastActive        : Optional[datetime | None] = Field(default=None, description="Last active time of the User")
    OnboardingSource  : Optional[str | None]      = Field(default=None, min_length=2, max_length=128, description="Source from where user came to the system")
    Role              : Optional[str | None]      = Field(default=None, min_length=2, max_length=128, description="Role of the User")
    Attributes        : Optional[dict | None]     = Field(default=None, description="Custom attributes of the User")
    TimezoneOffsetMin : Optional[int | None]      = Field(default=None, description="Timezone offset of the User")
    RegistrationDate  : Optional[datetime | None] = Field(default=None, description="Registration date of the User")


class UserSearchFilter(BaseSearchFilter):
    Attribute        : Optional[str]      = Field(description="Search by the attribute of the User")
    BirthDateBefore  : Optional[datetime] = Field(description="Search by the date before which the User was born")
    BirthDateAfter   : Optional[datetime] = Field(description="Search by the date after which the User was born")
    Gender           : Optional[str]      = Field(description="Search by the gender of the User")
    LastActiveBefore : Optional[datetime] = Field(description="Search by the date before which the User was last active")
    LastActiveAfter  : Optional[datetime] = Field(description="Search by the date after which the User was last active")
    RegisteredBefore : Optional[datetime] = Field(description="Search Users registered before the given date")
    RegisteredAfter  : Optional[datetime] = Field(description="Search Users registered after the given date")

class UserResponseModel(BaseModel):
    id                : UUID4                     = Field(description="Id of the User")
    TenantId          : UUID4                     = Field(description="Tenant Id of the User")
    BirthDate         : Optional[datetime | None] = Field(default=None, description="Birth date of the User")
    Gender            : str                       = Field(description="Gender of the User")
    LocationLongitude : Optional[float | None]    = Field(default=None, description="Longitude of the User")
    LocationLatitude  : Optional[float | None]    = Field(default=None, description="Latitude of the User")
    LastActive        : Optional[datetime | None] = Field(default=None, description="Last active time of the User")
    OnboardingSource  : Optional[str | None]      = Field(default=None, min_length=2, max_length=128, description="Source from where user came to the system")
    Role              : Optional[str | None]      = Field(default=None, min_length=2, max_length=128, description="Role of the User")
    Attributes        : Optional[dict | None]     = Field(default=None, description="Custom attributes of the User")
    TimezoneOffsetMin : Optional[int | None]      = Field(default=None, description="Timezone offset of the User")
    RegistrationDate  : Optional[datetime | None] = Field(default=None, description="Registration date of the User")
    CreatedAt         : datetime                  = Field(description="Created at")
    UpdatedAt         : datetime                  = Field(description="Updated at")
    DeletedAt         : Optional[datetime | None] = Field(default=None, description="Deleted at")

class UserSearchResults(BaseSearchResults):
    Items : List[UserResponseModel] = Field(description="List of Users")
