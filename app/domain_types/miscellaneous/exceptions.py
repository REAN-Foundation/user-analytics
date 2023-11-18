from fastapi import HTTPException, status
import traceback2 as traceback
from sqlalchemy.exc import SQLAlchemyError

###############################################################################

class HTTPError(HTTPException):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message

class InvalidUsage(HTTPError):
    def __init__(self, message: str):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.message = message

class Unauthorized(HTTPError):
    def __init__(self, message: str):
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.message = message

class Forbidden(HTTPError):
    def __init__(self, message: str):
        self.status_code = status.HTTP_403_FORBIDDEN
        self.message = message

class NotFound(HTTPError):
    def __init__(self, message: str):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.message = message

class MethodNotAllowed(HTTPError):
    def __init__(self, message: str):
        self.status_code = status.HTTP_405_METHOD_NOT_ALLOWED
        self.message = message

class NotAcceptable(HTTPError):
    def __init__(self, message: str):
        self.status_code = status.HTTP_406_NOT_ACCEPTABLE
        self.message = message

class RequestTimeout(HTTPError):
    def __init__(self, message: str):
        self.status_code = status.HTTP_408_REQUEST_TIMEOUT
        self.message = message

class Conflict(HTTPError):
    def __init__(self, message: str):
        self.status_code = status.HTTP_409_CONFLICT
        self.message = message

class Gone(HTTPError):
    def __init__(self, message: str):
        self.status_code = status.HTTP_410_GONE
        self.message = message

class ValidationError(HTTPError):
    def __init__(self, message: str):
        self.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        self.message = message

class UUIDValidationError(HTTPError):
    def __init__(self, message: str = "Provided id is not a valid UUID."):
        self.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        self.message = message

class InternalServerError(HTTPError):
    def __init__(self, message: str):
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        self.message = message

class NotImplemented(HTTPError):
    def __init__(self, message: str):
        self.status_code = status.HTTP_501_NOT_IMPLEMENTED
        self.message = message

class ServiceUnavailable(HTTPError):
    def __init__(self, message: str):
        self.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        self.message = message

class GatewayTimeout(HTTPError):
    def __init__(self, message: str):
        self.status_code = status.HTTP_504_GATEWAY_TIMEOUT
        self.message = message

class PreconditionFailed(HTTPError):
    def __init__(self, message: str):
        self.status_code = status.HTTP_412_PRECONDITION_FAILED
        self.message = message

class UnsupportedMediaType(HTTPError):
    def __init__(self, message: str):
        self.status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        self.message = message

class DbError(HTTPError):
    def __init__(self, message: str):
        super().__init__(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Database Error: {message}")

###############################################################################

class ServiceError:
    def __init__(self, exc: Exception, depth: int = 3):
        traces = self.get_traces(exc, depth, 0)
        message = ""
        if isinstance(exc, SQLAlchemyError):
            message = exc.orig
        else:
            message = hasattr(exc, "message") and exc.message or str(exc)
        status_code = hasattr(exc, "status_code") and exc.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR
        self.message = message
        self.traces = traces
        self.status_code = status_code

    def get_traces(self, exc:Exception, depth: int = 3, offset: int = 0):
        traces = traceback.format_exception(type(exc), exc, exc.__traceback__)
        traces.reverse()
        traces = traces[offset:depth]
        return traces

###############################################################################
