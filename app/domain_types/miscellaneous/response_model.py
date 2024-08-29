from pydantic import Field
from enum import Enum
from typing import TypeVar, Generic
from pydantic import BaseModel

T = TypeVar("T")

class ResponseStatusTypes(str, Enum):
    Success = "Success"
    Failure = "Failure"
    Error = "Error"

class ResponseModel(BaseModel, Generic[T]):
    Status: ResponseStatusTypes = Field(description="Status of the response", default=ResponseStatusTypes.Success)
    Message: str = ""
    Data: T | None = None
