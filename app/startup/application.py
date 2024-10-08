import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.domain_types.miscellaneous.exceptions import add_exception_handlers
from app.modules.data_sync.data_synchronizer import DataSynchronizer
from app.startup.client_auth_middleware import ClientAuthMiddleware
from app.startup.router import router
from app.startup.scheduler.job_scheduler import JobScheduler

#################################################################

def start():

    DataSynchronizer.populate_api_keys_cache()
    DataSynchronizer.populate_role_type_cache()
    DataSynchronizer.populate_tenants_cache()

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

    scheduler_thread = threading.Thread(target=JobScheduler.start_scheduler)
    scheduler_thread.start()

    return server

app = start()

#################################################################
add_exception_handlers(app)
#################################################################
