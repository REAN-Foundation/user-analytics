from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict

###############################################################################

class MessageEventType(str, Enum):
    USER_DELETE = "user.delete"

class EventMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")

    EventId  : Optional[str]            = None
    EventType: Optional[str]            = None
    Timestamp: Optional[str]            = None
    Payload  : Optional[Any]            = None
    Metadata : Optional[Dict[str, Any]] = None

class UserDeleteEventPayload(BaseModel):
    model_config = ConfigDict(extra="ignore")

    PatientUserId: Optional[str] = None
    TenantId     : Optional[str] = None
    TenantName   : Optional[str] = None
