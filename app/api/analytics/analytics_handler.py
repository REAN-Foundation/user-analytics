from datetime import date, timedelta
from typing import Optional
import asyncio

from pydantic import UUID4
from app.database.services.analytics.analyser import (
    calculate_basic_stats,
    calculate_tenant_engagement_metrics,
    calculate_feature_engagement_metrics
)

from app.domain_types.schemas.analytics import BasicAnalyticsStatistics, Demographics, UserEngagementMetrics
from app.modules.data_sync.data_synchronizer import DataSynchronizer
from app.telemetry.tracing import trace_span

###############################################################################

async def basic_stats_(
        tenant_id: Optional[UUID4] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None) -> BasicAnalyticsStatistics|None:
    try:
        return await calculate_basic_stats(tenant_id, start_date, end_date)
    except Exception as e:
        print(e)

async def calculate_tenant_engagement_metrics_(
                                    analysis_code,
                                    tenant_id: Optional[UUID4] = None,
                                    start_date: Optional[date] = None,
                                    end_date: Optional[date] = None):
    try:
        return await calculate_tenant_engagement_metrics(analysis_code, tenant_id, start_date, end_date)
    except Exception as e:
        print(e)

async def calculate_feature_engagement_metrics_(
                                    analysis_code,
                                    feature_name: str,
                                    tenant_id: Optional[UUID4] = None,
                                    start_date: Optional[date] = None,
                                    end_date: Optional[date] = None):
    try:
        return await calculate_feature_engagement_metrics(analysis_code, tenant_id, start_date, end_date)
    except Exception as e:
        print(e)

###############################################################################

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
