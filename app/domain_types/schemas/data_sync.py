from datetime import date
from typing import Optional
from pydantic import UUID4, BaseModel, Field

class DataSyncSearchFilter(BaseModel):
    StartDate  : Optional[date|None]  = Field(description="Start date for events", default=None)
    EndDate    : Optional[date|None]  = Field(description="End date for events", default=None)
