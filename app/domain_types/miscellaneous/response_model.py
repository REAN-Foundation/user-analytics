from pydantic import Field
from enum import Enum
from typing import TypeVar, Generic
from pydantic.generics import GenericModel

T = TypeVar("T")

class ResponseStatusTypes(str, Enum):
    Success = "Success"
    Failure = "Failure"
    Error = "Error"

class ResponseModel(GenericModel, Generic[T]):
    Status: ResponseStatusTypes = Field(description="Status of the response", default=ResponseStatusTypes.Success)
    Message: str = ""
    Data: T | None = None
