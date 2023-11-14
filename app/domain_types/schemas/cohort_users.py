from datetime import datetime
from typing import List, Optional
from pydantic import UUID4, BaseModel, Field

class CohortUserCreateModel(BaseModel):
    CohortId         : UUID4              = Field(description="Id of the Cohort")
    UserId           : UUID4              = Field(description="Id of the User")
    TenantId         : UUID4              = Field(description="Tenant Id of the User")
    TimestampAdded   : datetime           = Field(default=None, description="Timestamp of the Event")
    TimestampRemoved : Optional[datetime] = Field(default=None, description="Timestamp of the Event")
