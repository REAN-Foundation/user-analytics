from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.domain_types.miscellaneous.exceptions import add_exception_handlers
from app.modules.data_sync_handler import DataSyncHandler
from app.startup.client_auth_middleware import ClientAuthMiddleware
from app.startup.router import router

#################################################################

def start():

    DataSyncHandler.populate_api_keys_cache()

    server = FastAPI()

    # Add CORS middleware
    server.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    server.add_middleware(ClientAuthMiddleware)
    server.include_router(router)

    return server

app = start()

#################################################################
add_exception_handlers(app)
#################################################################
