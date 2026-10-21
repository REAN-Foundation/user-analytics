import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.common.logger import logger
from app.config.config import get_settings
from app.domain_types.miscellaneous.exceptions import add_exception_handlers
from app.modules.data_sync.data_synchronizer import DataSynchronizer
from app.modules.events.event_consumer_factory import get_event_consumer
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

    start_event_consumer(server)

    return server

def start_event_consumer(server: FastAPI):
    if not get_settings().MESSAGING_ENABLED:
        return
    try:
        consumer = get_event_consumer()
        if consumer is None:
            return
        consumer.start_listening()
        server.add_event_handler("shutdown", consumer.close)
    except Exception as e:
        logger.error(f"Error starting event consumer: {e}")

app = start()

#################################################################
add_exception_handlers(app)
#################################################################
