from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request, status
from app.common.logger import logger
from app.common.utils import print_colorized_json
from app.domain_types.miscellaneous.exceptions import HTTPError, ServiceError
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import SQLAlchemyError
import traceback2 as traceback
from app.startup.router import router

#################################################################

def get_application():

    server = FastAPI()

    # Add CORS middleware
    server.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    server.include_router(router)

    return server

app = get_application()

#################################################################

@app.exception_handler(HTTPError)
async def api_error_handler(request: Request, exc: HTTPError):

    err_obj = ServiceError(exc)
    print_colorized_json(err_obj)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "Message": exc.message,
            "Status": "Failure",
            "Data" : None
        },
    )

# Validation Errors

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):

    err_obj = ServiceError(exc)
    print_colorized_json(err_obj)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            {
                "Message": "Validation Error",
                "Status": "Failure",
                "Errors": exc.errors(), 
                                "RequestBody": exc.body
            }
        ),
    )

# Database Errors

@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    
    err_obj = ServiceError(exc)
    print_colorized_json(err_obj)

    # Return a generic error message to the client
    # Do not return the actual error message to the client
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder(
            {
                "Message": "Database Error",
                "Status": "Failure",
                "Errors": exc.args,
            }
        ),
    )

# Generic Errors

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # Handle telemetry and logging here...
    logger.error(f"Internal Server Error: {exc.args}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder(
            {
                "Message": "Internal Server Error",
                "Status": "Failure",
                "Errors": exc.args,
            }
        ),
    )
