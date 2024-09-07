import os
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, status, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import UUID4
from app.api.analytics.analytics_handler import (
    basic_stats_,
    download_feature_engagement_metrics_,
    generate_feature_engagement_metrics_,
    calculate_tenant_engagement_metrics_,
    download_user_engagement_metrics_,
    get_feature_engagement_metrics_,
    get_user_engagement_metrics_
)
from app.common.utils import generate_random_code
from app.database.database_accessor import get_db_session
from app.domain_types.miscellaneous.response_model import ResponseModel, ResponseStatusTypes
from app.domain_types.schemas.analytics import (
    BasicAnalyticsStatistics,
    FeatureEngagementMetrics,
    FeatureEngagementMetricsResponse,
    UserEngagementMetrics,
    UserEngagementMetricsResponse
)

###############################################################################

router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

###############################################################################

@router.get("/basic-stats",
            status_code=status.HTTP_200_OK,
            response_model=ResponseModel[BasicAnalyticsStatistics|None])
async def basic_stats(
        tenant_id: Optional[UUID4] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None):
    stats = await basic_stats_(tenant_id, start_date, end_date)
    message = "Basic analytics statistics retrieved successfully."
    resp = ResponseModel[BasicAnalyticsStatistics](Message=message, Data=stats)
    return resp

###############################################################################

@router.get("/generate-user-engagement-metrics",
            status_code=status.HTTP_200_OK,
            response_model=ResponseModel[UserEngagementMetricsResponse|None])
async def generate_user_engagement_metrics(
        background_tasks: BackgroundTasks,
        tenant_id: Optional[UUID4] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None):

    analysis_code = generate_random_code(12)
    base_url = os.getenv("BASE_URL")

    background_tasks.add_task(calculate_tenant_engagement_metrics_, analysis_code, tenant_id, start_date, end_date)

    res_model = UserEngagementMetricsResponse(
        TenantId     = tenant_id if tenant_id is not None else "Unspecified",
        StartDate    = start_date if start_date is not None else "Unspecified",
        EndDate      = end_date if end_date is not None else "Unspecified",
        AnalysisCode = analysis_code,
        JsonURL      = f"{base_url}/api/analytics/download-user-engagement-metrics/{analysis_code}/format/json",
        ExcelURL     = f"{base_url}/api/analytics/download-user-engagement-metrics/{analysis_code}/format/excel",
        PDFURL       = f"{base_url}/api/analytics/download-user-engagement-metrics/{analysis_code}/format/pdf",
        URL          = f"{base_url}/api/analytics/user-engagement-metrics/{analysis_code}"
    )
    message = "User engagement metrics analysis started successfully. It may take a while to complete. You can access the results through the urls shared."
    resp = ResponseModel[UserEngagementMetricsResponse](Message=message, Data=res_model)
    return resp

@router.get("/download-user-engagement-metrics/{analysis_code}/format/{file_format}",
            status_code=status.HTTP_200_OK)
def download_user_engagement_metrics(analysis_code: str, file_format: str):
    file_format_lower = file_format.lower()
    if file_format_lower not in ["json", "excel", "pdf"]:
        raise HTTPException(status_code=400, detail="Invalid file format. Supported formats are 'json', 'excel' and 'pdf'.")
    stream = download_user_engagement_metrics_(analysis_code, file_format_lower)
    return StreamingResponse(stream, media_type="application/octet-stream")

@router.get("/user-engagement-metrics/{analysis_code}",
            status_code=status.HTTP_200_OK,
            response_model=ResponseModel[UserEngagementMetrics|None])
def get_user_engagement_metrics_(analysis_code: str):
    metrics = get_user_engagement_metrics_(analysis_code)
    message = "User engagement metrics retrieved successfully."
    resp = ResponseModel[UserEngagementMetrics](Message=message, Data=metrics)
    return resp

###############################################################################

@router.get("/generate-feature-engagement-metrics/{feature}",
            status_code=status.HTTP_200_OK,
            response_model=ResponseModel[FeatureEngagementMetricsResponse|None])
def generate_feature_engagement_metrics(
        background_tasks: BackgroundTasks,
        feature: str,
        tenant_id: Optional[UUID4] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None):
    analysis_code = generate_random_code(12)
    base_url = os.getenv("BASE_URL")
    res_model = FeatureEngagementMetricsResponse(
        TenantId=tenant_id,
        StartDate=start_date,
        EndDate=end_date,
        AnalysisCode=analysis_code,
        JsonURL=f"{base_url}/api/analytics/download-feature-engagement-metrics/{analysis_code}/format/json",
        ExcelURL=f"{base_url}/api/analytics/download-feature-engagement-metrics/{analysis_code}/format/excel",
        PDFURL=f"{base_url}/api/analytics/download-feature-engagement-metrics/{analysis_code}/format/pdf",
        URL=f"{base_url}/api/analytics/feature-engagement-metrics/{analysis_code}"
    )
    background_tasks.add_task(generate_feature_engagement_metrics_(analysis_code, feature, tenant_id, start_date, end_date))
    message = "Feature engagement metrics analysis started successfully. It may take a while to complete. You can access the results through the urls shared."
    resp = ResponseModel[bool](Message=message, Data=res_model)
    return resp

@router.get("/download-feature-engagement-metrics/{analysis_code}/format/{file_format}",
            status_code=status.HTTP_200_OK)
def download_feature_engagement_metrics(analysis_code: str, file_format: str):
    file_format_lower = file_format.lower()
    if file_format_lower not in ["json", "excel", "pdf"]:
        raise HTTPException(status_code=400, detail="Invalid file format. Supported formats are 'json', 'excel' and 'pdf'.")
    stream = download_feature_engagement_metrics_(analysis_code, file_format_lower)
    return StreamingResponse(stream, media_type="application/octet-stream")

@router.get("/feature-engagement-metrics/{analysis_code}",
            status_code=status.HTTP_200_OK,
            response_model=ResponseModel[FeatureEngagementMetrics|None])
def feature_engagement_metrics(analysis_code: str):
    metrics = get_feature_engagement_metrics_(analysis_code)
    message = "Feature engagement metrics retrieved successfully."
    resp = ResponseModel[FeatureEngagementMetrics](Message=message, Data=metrics)
    return resp

###############################################################################
