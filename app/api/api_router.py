from fastapi import APIRouter
from app.config.constants import API_PREFIX
from .event.event_routes import router as event_router
from .cohort.cohort_routes import router as cohort_router
from .filter.filter_routes import router as filter_router
from .user.user_routes import router as user_router
from .user_milestone.user_milestone_routes import router as user_milestone_router
from .tenant_milestone.tenant_milestone_routes import router as tenant_milestone_router
from .sync.sync_routes import router as sync_router
from .analytics.analytics_routes import router as analytics_router

router = APIRouter(prefix=API_PREFIX)

def add_routes():
    router.include_router(event_router)
    router.include_router(cohort_router)
    router.include_router(filter_router)
    router.include_router(user_router)
    router.include_router(user_milestone_router)
    router.include_router(tenant_milestone_router)
    router.include_router(sync_router)
    router.include_router(analytics_router)

    # Add other routes here

add_routes()
