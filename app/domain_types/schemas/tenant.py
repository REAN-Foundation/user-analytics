from datetime import datetime
from typing import Any, List, Optional
from pydantic import UUID4, BaseModel, Field
from app.domain_types.schemas.base_types import BaseSearchFilter, BaseSearchResults

class TenantCreateModel(BaseModel):
    TenantName       : str                = Field(min_length=2, max_length=256, description="Name of the Tenant")
    TenantCode       : str                = Field(min_length=2, max_length=256, description="Code of the Tenant")
    RegistrationDate : datetime           = Field(default=None, description="Registration Date")
    Attributes       : Optional[Any|None] = Field(default=None, description="Attributes of the Tenant")

TenantCreateModel.update_forward_refs()

class TenantUpdateModel(BaseModel):
    TenantName       : Optional[str]      = Field(min_length=2, max_length=256, description="Name of the Tenant")
    TenantCode       : Optional[str]      = Field(min_length=2, max_length=256, description="Code of the Tenant")
    RegistrationDate : Optional[datetime] = Field(default=None, description="Registration Date")
    Attributes       : Optional[Any|None] = Field(default=None, description="Attributes of the Tenant")

TenantUpdateModel.update_forward_refs()

class TenantSearchFilter(BaseSearchFilter):
    TenantName       : Optional[str]
    TenantCode       : Optional[str]

TenantSearchFilter.update_forward_refs()

class TenantResponseModel(BaseModel):
    id               : UUID4              = Field(description="Id of the Tenant")
    TenantName       : str                = Field(min_length=2, max_length=256, description="Name of the Tenant")
    TenantCode       : str                = Field(min_length=2, max_length=256, description="Code of the Tenant")
    RegistrationDate : datetime           = Field(default=None, description="Registration Date")
    Attributes       : Optional[Any|None] = Field(default=None, description="Attributes of the Tenant")

TenantResponseModel.update_forward_refs()

class TenantSearchResults(BaseSearchResults):
    Items: List[TenantResponseModel] = []
