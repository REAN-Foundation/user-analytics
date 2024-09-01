from typing import Optional
from app.common.validators import validate_uuid4
from app.modules.data_sync_handler import DataSyncHandler
from app.telemetry.tracing import trace_span

###############################################################################

@trace_span("handler: sync_users")
def sync_users_():
    try:
        DataSyncHandler.sync_users()
    except Exception as e:
        print(e)

@trace_span("handler: sync_user_login_session_events")
def sync_user_login_session_events_():
    try:
        DataSyncHandler.sync_user_login_events()
    except Exception as e:
        print(e)

