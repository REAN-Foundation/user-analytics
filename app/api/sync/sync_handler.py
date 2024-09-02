from typing import Optional
from app.common.validators import validate_uuid4
from app.modules.data_sync.data_synchronizer import DataSynchronizer
from app.telemetry.tracing import trace_span

###############################################################################

@trace_span("handler: sync_users")
def sync_users_():
    try:
        # Please note that there are users with patient role
        # but there is no corresponding entry in the patients table
        # So such users are not synched.
        DataSynchronizer.sync_users()
    except Exception as e:
        print(e)

@trace_span("handler: sync_user_login_session_events")
def sync_user_login_session_events_():
    try:
        DataSynchronizer.sync_user_login_events()
    except Exception as e:
        print(e)

@trace_span("handler: sync_user_medication_create_events")
def sync_user_medication_create_events_():
    try:
        DataSynchronizer.sync_user_medication_create_events()
    except Exception as e:
        print(e)

@trace_span("handler: sync_user_medication_update_events")
def sync_user_medication_update_events_():
    try:
        DataSynchronizer.sync_user_medication_update_events()
    except Exception as e:
        print(e)

@trace_span("handler: sync_user_medication_delete_events")
def sync_user_medication_delete_events_():
    try:
        DataSynchronizer.sync_user_medication_delete_events()
    except Exception as e:
        print(e)

@trace_span("handler: sync_user_medication_schedule_taken_events")
def sync_user_medication_schedule_taken_events_():
    try:
        DataSynchronizer.sync_user_medication_schedule_taken_events()
    except Exception as e:
        print(e)

@trace_span("handler: sync_user_medication_schedule_missed_events")
def sync_user_medication_schedule_missed_events_():
    try:
        DataSynchronizer.sync_user_medication_schedule_missed_events()
    except Exception as e:
        print(e)

