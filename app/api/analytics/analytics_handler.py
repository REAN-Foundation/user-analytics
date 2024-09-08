from app.database.services.analytics.analyser import (
    calculate,
    calculate_basic_stats,
    calculate_generic_engagement_metrics,
    calculate_feature_engagement_metrics
)
from app.domain_types.schemas.analytics import (
    AnalyticsFilters,
    BasicAnalyticsStatistics,
    EngagementMetrics,
    FeatureEngagementMetrics,
    GenericEngagementMetrics
)
from app.telemetry.tracing import trace_span

###############################################################################

async def calculate_(analysis_code:str, filters: AnalyticsFilters|None) -> EngagementMetrics|None:
    return await calculate(analysis_code, filters)

async def calculate_basic_statistics_(filters: AnalyticsFilters|None) -> BasicAnalyticsStatistics|None:
    return await calculate_basic_stats(filters)

async def calculate_generic_engagement_metrics_(filters: AnalyticsFilters|None) -> GenericEngagementMetrics|None:
    return await calculate_generic_engagement_metrics(filters)

async def calculate_feature_engagement_metrics_(feature: str, filters: AnalyticsFilters|None) -> FeatureEngagementMetrics|None:
    return await calculate_feature_engagement_metrics(feature, filters)

###############################################################################

@trace_span("handler: download_metrics")
def download_metrics_(analysis_code:str):
    try:
        pass
    except Exception as e:
        print(e)

@trace_span("handler: get_metrics")
def get_metrics_(analysis_code:str):
    try:
        pass
    except Exception as e:
        print(e)

###############################################################################
