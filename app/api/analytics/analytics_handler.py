import os
from app.common.utils import print_exception
from app.database.services.analytics.analysis_service import (
    calculate,
    calculate_basic_stats,
    calculate_generic_engagement_metrics,
    calculate_feature_engagement_metrics,
    get_analysis_by_code,
    get_analysis_code
)
from app.domain_types.miscellaneous.exceptions import HTTPError
from app.domain_types.schemas.analytics import (
    AnalyticsFilters,
    BasicAnalyticsStatistics,
    EngagementMetrics,
    FeatureEngagementMetrics,
    GenericEngagementMetrics
)
from app.modules.storage.provider.awa_s3_storage_service import AwsS3StorageService
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
async def download_metrics_(analysis_code:str, file_format_lower: str):
    try:
        if file_format_lower == 'excel':
            file_format_lower = 'xlsx'
        storage_key = f"analytics_report_{analysis_code}.{file_format_lower}"
        storage_service = AwsS3StorageService()
        content =  await storage_service.download_file_as_stream(storage_key)
        if content is None:
            raise Exception(message='Unable to download report!')
        return content
    except Exception as e:
        print_exception(e)
        raise HTTPError(status_code=500, message='Unable to download report!')

@trace_span("handler: get_metrics")
def get_metrics_(analysis_code:str):
    try:
        analysis = get_analysis_by_code(analysis_code)
        return analysis
    except Exception as e:
        print_exception(e)

###############################################################################

async def get_analysis_code_() -> str:
    return await get_analysis_code()

###############################################################################
