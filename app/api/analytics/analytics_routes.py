import os
from fastapi import APIRouter, status, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from app.api.analytics.analytics_handler import (
    calculate_,
    calculate_basic_statistics_,
    calculate_feature_engagement_metrics_,
    calculate_generic_engagement_metrics_,
    download_metrics_,
    get_metrics_,
    get_analysis_code_
)
from app.common.utils import generate_random_code
from app.database.services.analytics.analysis_service import check_filter_params
from app.domain_types.miscellaneous.response_model import ResponseModel
from app.domain_types.schemas.analytics import (
    AnalyticsFilters,
    BasicAnalyticsStatistics,
    EngagementMetrics,
    FeatureEngagementMetrics,
    GenericEngagementMetrics,
    CalculateMetricsResponse
)

###############################################################################

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

###############################################################################

@router.get("/basic-statistics",
            status_code=status.HTTP_200_OK,
            response_model=ResponseModel[BasicAnalyticsStatistics|None])
async def calculate_basic_statistics(filters: AnalyticsFilters):
    stats = await calculate_basic_statistics_(filters)
    message = "Basic analytics statistics retrieved successfully."
    resp = ResponseModel[BasicAnalyticsStatistics](Message=message, Data=stats)
    return resp

@router.get("/generic-engagement-metrics",
            status_code=status.HTTP_200_OK,
            response_model=ResponseModel[GenericEngagementMetrics|None])
async def calculate_generic_engagement_metrics(filters: AnalyticsFilters):
    metrics = await calculate_generic_engagement_metrics_(filters)
    message = "Generic engagement metrics retrieved successfully."
    resp = ResponseModel[GenericEngagementMetrics](Message=message, Data=metrics)
    return resp

@router.get("/feature-engagement-metrics/{feature}",
            status_code=status.HTTP_200_OK,
            response_model=ResponseModel[FeatureEngagementMetrics|None])
async def calculate_feature_engagement_metrics(feature: str, filters: AnalyticsFilters):
    metrics = await calculate_feature_engagement_metrics_(feature, filters)
    message = "Feature engagement metrics retrieved successfully."
    resp = ResponseModel[FeatureEngagementMetrics](Message=message, Data=metrics)
    return resp
###############################################################################

@router.post("/metrics",
            status_code=status.HTTP_200_OK,
            response_model=ResponseModel[CalculateMetricsResponse|None])
async def calculate_metrics(
        background_tasks: BackgroundTasks,
        filters: AnalyticsFilters):

    analysis_code = get_analysis_code_()
    base_url = os.getenv("BASE_URL")
    filters_updated = check_filter_params(filters)

    background_tasks.add_task(calculate_, analysis_code, filters_updated)

    res_model = CalculateMetricsResponse(
        TenantId     = filters_updated.TenantId,
        RoleId       = filters_updated.RoleId,
        StartDate    = str(filters_updated.StartDate),
        EndDate      = str(filters_updated.EndDate),
        AnalysisCode = analysis_code,
        JsonURL      = f"{base_url}/api/analytics/download/{analysis_code}/formats/json",
        ExcelURL     = f"{base_url}/api/analytics/download/{analysis_code}/formats/excel",
        PdfURL       = f"{base_url}/api/analytics/download/{analysis_code}/formats/pdf",
        URL          = f"{base_url}/api/analytics/metrics/{analysis_code}"
    )
    message = "Engagement metrics analysis started successfully. It may take a while to complete. You can access the results through the urls shared."
    resp = ResponseModel[CalculateMetricsResponse](Message=message, Data=res_model)
    return resp

@router.get("/metrics/{analysis_code}",
            status_code=status.HTTP_200_OK,
            response_model=ResponseModel[EngagementMetrics|None])
async def get_metrics(analysis_code: str):
    metrics = await get_metrics_(analysis_code)
    message = "Engagement metrics retrieved successfully."
    resp = ResponseModel[EngagementMetrics](Message=message, Data=metrics)
    return resp

@router.get("/download/{analysis_code}/formats/{file_format}",
            status_code=status.HTTP_200_OK)
def download_user_engagement_metrics(analysis_code: str, file_format: str):
    file_format_lower = file_format.lower()
    if file_format_lower not in ["json", "excel", "pdf"]:
        raise HTTPException(status_code=400, detail="Invalid file format. Supported formats are 'json', 'excel' and 'pdf'.")
    stream = download_metrics_(analysis_code, file_format_lower)
    return StreamingResponse(stream, media_type="application/octet-stream")

###############################################################################
