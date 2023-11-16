from fastapi import APIRouter
from app.config.constants import API_PREFIX
from .event.event_routes import router as event_router
from .cohort.cohort_routes import router as cohort_router
from .filter.filter_routes import router as filter_router
from .user.user_routes import router as user_router

router = APIRouter(prefix=API_PREFIX)

def add_routes():
    router.include_router(event_router)
    router.include_router(cohort_router)
    router.include_router(filter_router)
    router.include_router(user_router)

    # Add other routes here

add_routes()
