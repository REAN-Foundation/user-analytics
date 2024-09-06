from datetime import date, timedelta
from typing import Optional
import asyncio

from pydantic import UUID4
from app.database.services.analytics.basic_stats import (
    get_all_registered_patients,
    get_all_registered_users,
    get_current_active_patients,
    get_patient_age_demographics,
    get_patient_deregistration_history_by_months,
    get_patient_ethnicity_demographics,
    get_patient_gender_demographics,
    get_patient_healthsystem_distribution,
    get_patient_hospital_distribution,
    get_patient_race_demographics,
    get_patient_registration_hisory_by_months,
    get_patient_survivor_or_caregiver_distribution
)
from app.database.services.analytics.user_engagement import (
    get_daily_active_patients,
    get_monthly_active_patients,
    get_patient_stickiness_dau_mau,
    get_patients_average_session_length_in_minutes,
    get_patients_login_frequency,
    get_patients_most_commonly_used_features,
    get_patients_retention_rate_in_specific_time_interval,
    get_patients_retention_rate_on_specific_days,
    get_weekly_active_patients
)
from app.database.services.analytics.report_generator_excel import generate_user_engagement_report_excel
from app.database.services.analytics.report_generator_json import generate_user_engagement_report_json
from app.database.services.analytics.report_generator_pdf import generate_user_engagement_report_pdf
from app.domain_types.schemas.analytics import BasicAnalyticsStatistics, Demographics, UserEngagementMetrics
from app.modules.data_sync.data_synchronizer import DataSynchronizer
from app.telemetry.tracing import trace_span

###############################################################################
PAST_DAYS_TO_CONSIDER = 540
###############################################################################

@trace_span("handler: basic_stats")
async def basic_stats_(
        tenant_id: Optional[UUID4] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None) -> BasicAnalyticsStatistics|None:
    try:

        tenant_id, start_date, end_date, tenant_name = check_params(tenant_id, start_date, end_date)

        results = await asyncio.gather(
            get_all_registered_users(tenant_id, start_date, end_date),
            get_all_registered_patients(tenant_id, start_date, end_date),
            get_current_active_patients(tenant_id),
            get_patient_registration_hisory_by_months(tenant_id, start_date, end_date),
            get_patient_deregistration_history_by_months(tenant_id, start_date, end_date),
            get_patient_age_demographics(tenant_id, start_date, end_date),
            get_patient_gender_demographics(tenant_id, start_date, end_date),
            get_patient_ethnicity_demographics(tenant_id, start_date, end_date),
            get_patient_race_demographics(tenant_id, start_date, end_date),
            get_patient_healthsystem_distribution(tenant_id, start_date, end_date),
            get_patient_hospital_distribution(tenant_id, start_date, end_date),
            get_patient_survivor_or_caregiver_distribution(tenant_id, start_date, end_date)
        )

        total_users = results[0]
        total_patients = results[1]
        active_patients = results[2]
        registration_history = results[3]
        deregistration_history = results[4]
        age_demographics = results[5]
        gender_demographics = results[6]
        ethnicity_demographics = results[7]
        race_demographics = results[8]
        healthsystem_distribution = results[9]
        hospital_distribution = results[10]
        survivor_or_caregiver_distribution = results[11]

        demographics = Demographics(
            AgeGroups                       = age_demographics,
            GenderGroups                    = gender_demographics,
            LocationGroups                  = [],
            EthnicityGroups                 = ethnicity_demographics,
            RaceGroups                      = race_demographics,
            HealthSystemDistribution        = healthsystem_distribution,
            HospitalDistribution            = hospital_distribution,
            SurvivorOrCareGiverDistribution = survivor_or_caregiver_distribution
        )

        stats = BasicAnalyticsStatistics(
            TenantId=tenant_id,
            TenantName=tenant_name,
            StartDate=start_date,
            EndDate=end_date,
            TotalUsers=total_users,
            TotalPatients=total_patients,
            TotalActivePatients=active_patients,
            PatientRegistrationHistory=registration_history,
            PatientDeregistrationHistory=deregistration_history,
            PatientDemographics=demographics,
        )

        return stats

    except Exception as e:
        print(e)

###############################################################################

# @trace_span("handler: generate_user_engagement_metrics")
async def generate_user_engagement_metrics_(
                                    analysis_code,
                                    tenant_id: Optional[UUID4] = None,
                                    start_date: Optional[date] = None,
                                    end_date: Optional[date] = None):
    try:
        json_file_path, excel_file_path, pdf_file_path = await user_engagement(analysis_code, tenant_id, start_date, end_date)

        print(f"JSON file path: {json_file_path}")
        print(f"Excel file path: {excel_file_path}")
        print(f"PDF file path: {pdf_file_path}")

    except Exception as e:
        print(e)

async def user_engagement(analysis_code, tenant_id, start_date, end_date):
    tenant_id, start_date, end_date, tenant_name = check_params(tenant_id, start_date, end_date)


    results = await asyncio.gather(
            get_daily_active_patients(tenant_id, start_date, end_date),
            get_weekly_active_patients(tenant_id, start_date, end_date),
            get_monthly_active_patients(tenant_id, start_date, end_date),
            get_patients_average_session_length_in_minutes(tenant_id, start_date, end_date),
            get_patients_login_frequency(tenant_id, start_date, end_date),
            get_patients_retention_rate_on_specific_days(tenant_id, start_date, end_date),
            get_patients_retention_rate_in_specific_time_interval(tenant_id, start_date, end_date),
            get_patient_stickiness_dau_mau(tenant_id, start_date, end_date),
            get_patients_most_commonly_used_features(tenant_id, start_date, end_date)
            # get_patients_most_commonly_visited_screens(tenant_id, start_date, end_date),
        )

    daily_active_users = results[0]
    weekly_active_users = results[1]
    monthly_active_users = results[2]
    average_session_length = results[3]
    login_frequency = results[4]
    retention_rate_on_specific_days = results[5]
    retention_rate_in_specific_intervals = results[6]
    stickiness_ratio = results[7]
    most_common_features = results[8]
    # most_commonly_visited_screens = results[8]

    user_engagement_metrics = UserEngagementMetrics(
            TenantId=tenant_id,
            TenantName=tenant_name,
            StartDate=str(start_date) if start_date else 'Unspecified',
            EndDate=str(end_date) if end_date else 'Unspecified',
            DailyActiveUsers=daily_active_users,
            WeeklyActiveUsers=weekly_active_users,
            MonthlyActiveUsers=monthly_active_users,
            AverageSessionLengthMinutes=average_session_length,
            LoginFrequency=login_frequency,
            RetentionRateOnSpecificDays=retention_rate_on_specific_days,
            RetentionRateInSpecificIntervals=retention_rate_in_specific_intervals,
            StickinessRatio=stickiness_ratio,
            MostCommonlyVisitedFeatures=most_common_features
        )

    json_file_path = await generate_user_engagement_report_json(analysis_code, user_engagement_metrics)
    # excel_file_path = generate_user_engagement_report_excel(analysis_code, user_engagement_metrics)
    # pdf_file_path = generate_user_engagement_report_pdf(analysis_code, user_engagement_metrics)
    excel_file_path = None
    pdf_file_path = None

    return json_file_path, excel_file_path, pdf_file_path

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

def check_params(tenant_id, start_date, end_date):
    if not start_date:
        start_date = date.today() - timedelta(days=PAST_DAYS_TO_CONSIDER)
    if not end_date:
        end_date = date.today()

    tenant_name = "unspecified"
    if not tenant_id:
        return tenant_id,start_date,end_date,tenant_name
        # tenant = DataSynchronizer.get_tenant_by_code('default')
        # if tenant is not None:
        #     tenant_id = tenant['id']
        #     tenant_name = tenant['TenantName']
    else:
        tenant = DataSynchronizer.get_tenant(tenant_id)
        if tenant is not None:
            tenant_name = tenant['TenantName']
    return tenant_id,start_date,end_date,tenant_name

