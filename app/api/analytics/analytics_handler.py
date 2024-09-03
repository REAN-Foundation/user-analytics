from typing import Optional
from app.common.validators import validate_uuid4
from app.modules.data_sync.data_synchronizer import DataSynchronizer
from app.modules.data_sync.login_events_synchonizer import LoginEventsSynchronizer
from app.modules.data_sync.medication_events_synchronizer import MedicationEventsSynchronizer
from app.telemetry.tracing import trace_span

###############################################################################

@trace_span("handler: basic_stats")
def basic_stats_():
    try:
        pass
    except Exception as e:
        print(e)

###############################################################################

@trace_span("handler: generate_user_engagement_metrics")
def generate_user_engagement_metrics_():
    try:
        pass
    except Exception as e:
        print(e)

@trace_span("handler: download_user_engagement_metrics")
def download_user_engagement_metrics_():
    try:
        pass
    except Exception as e:
        print(e)

@trace_span("handler: get_user_engagement_metrics")
def get_user_engagement_metrics_():
    try:
        pass
    except Exception as e:
        print(e)

###############################################################################

@trace_span("handler: generate_feature_engagement_metrics")
def generate_feature_engagement_metrics_():
    try:
        pass
    except Exception as e:
        print(e)

@trace_span("handler: download_feature_engagement_metrics")
def download_feature_engagement_metrics_():
    try:
        pass
    except Exception as e:
        print(e)

@trace_span("handler: get_feature_engagement_metrics")
def get_feature_engagement_metrics_():
    try:
        pass
    except Exception as e:
        print(e)

###############################################################################
