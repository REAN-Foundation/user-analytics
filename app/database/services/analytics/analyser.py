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
    get_patients_most_commonly_visited_screens,
    get_patients_retention_rate_in_specific_time_interval,
    get_patients_retention_rate_on_specific_days,
    get_weekly_active_patients
)
from app.database.services.analytics.feature_engagement import (
    get_feature_access_frequency,
    get_feature_engagement_rate,
    get_feature_retention_rate_on_specific_days,
    get_feature_retention_rate_in_specific_intervals,
    get_feature_average_usage_duration_minutes,
    get_feature_drop_off_points,
)
from app.database.services.analytics.reports.report_generator_excel import generate_user_engagement_report_excel
from app.database.services.analytics.reports.report_generator_json import generate_user_engagement_report_json
from app.database.services.analytics.reports.report_generator_pdf import generate_user_engagement_report_pdf
from app.domain_types.schemas.analytics import BasicAnalyticsStatistics, Demographics, FeatureEngagementMetrics, TenantEngagementMetrics, GenericEngagementMetrics
from app.modules.data_sync.data_synchronizer import DataSynchronizer
from app.telemetry.tracing import trace_span

###############################################################################
PAST_DAYS_TO_CONSIDER = 540
###############################################################################

async def calculate(
        analysis_code: str,
        tenant_id: Optional[UUID4] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None) -> BasicAnalyticsStatistics|None:

    print(f"Analysis started -> {analysis_code} -> ?For tenant: {tenant_id} from {start_date} to {end_date}")

    try:
        basic_stats = await calculate_basic_stats(tenant_id, start_date, end_date)
        tenant_overall_engagement = await calculate_tenant_engagement_metrics(tenant_id, start_date, end_date)
        features = [
            'feature1',
            'feature2',
            'feature3',
            'feature4',
            'feature5'
        ]
        feature_engagement = []
        for feature in features:
            engament = await calculate_feature_engagement_metrics(
                feature, tenant_id, start_date, end_date)
            feature_engagement.append(engament)

        metrics = TenantEngagementMetrics(
            TenantId=tenant_id,
            TenantName=basic_stats.TenantName,
            StartDate=start_date,
            EndDate=end_date,
            BasicStats=basic_stats,
            TenantOverallEngagement=tenant_overall_engagement,
            FeatureEngagement=feature_engagement
        )

        # await generate_reports(analysis_code, metrics)

        return metrics

    except Exception as e:
        print(e)

###############################################################################

async def calculate_basic_stats(
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

        total_users                        = results[0]
        total_patients                     = results[1]
        active_patients                    = results[2]
        registration_history               = results[3]
        deregistration_history             = results[4]
        age_demographics                   = results[5]
        gender_demographics                = results[6]
        ethnicity_demographics             = results[7]
        race_demographics                  = results[8]
        healthsystem_distribution          = results[9]
        hospital_distribution              = results[10]
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
            TenantId                     = tenant_id,
            TenantName                   = tenant_name,
            StartDate                    = start_date,
            EndDate                      = end_date,
            TotalUsers                   = total_users,
            TotalPatients                = total_patients,
            TotalActivePatients          = active_patients,
            PatientRegistrationHistory   = registration_history,
            PatientDeregistrationHistory = deregistration_history,
            PatientDemographics          = demographics,
        )

        return stats

    except Exception as e:
        print(e)

async def calculate_tenant_engagement_metrics(
                                    tenant_id: Optional[UUID4] = None,
                                    start_date: Optional[date] = None,
                                    end_date: Optional[date] = None):
    try:
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
                get_patients_most_commonly_used_features(tenant_id, start_date, end_date),
                get_patients_most_commonly_visited_screens(tenant_id, start_date, end_date)
            )

        daily_active_users                   = results[0]
        weekly_active_users                  = results[1]
        monthly_active_users                 = results[2]
        average_session_length               = results[3]
        login_frequency                      = results[4]
        retention_rate_on_specific_days      = results[5]
        retention_rate_in_specific_intervals = results[6]
        stickiness_ratio                     = results[7]
        most_common_features                 = results[8]
        most_commonly_visited_screens        = results[9]

        user_engagement_metrics = GenericEngagementMetrics(
                TenantId                         = tenant_id,
                TenantName                       = tenant_name,
                StartDate                        = str(start_date) if start_date else 'Unspecified',
                EndDate                          = str(end_date) if end_date else 'Unspecified',
                DailyActiveUsers                 = daily_active_users,
                WeeklyActiveUsers                = weekly_active_users,
                MonthlyActiveUsers               = monthly_active_users,
                AverageSessionLengthMinutes      = average_session_length,
                LoginFrequency                   = login_frequency,
                RetentionRateOnSpecificDays      = retention_rate_on_specific_days,
                RetentionRateInSpecificIntervals = retention_rate_in_specific_intervals,
                StickinessRatio                  = stickiness_ratio,
                MostCommonlyVisitedFeatures      = most_common_features,
                MostCommonlyVisitedScreens       = most_commonly_visited_screens
            )

        return user_engagement_metrics

    except Exception as e:
        print(e)


async def calculate_feature_engagement_metrics(
        feature: str,
        tenant_id: Optional[UUID4] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None)-> FeatureEngagementMetrics|None:
    try:
        tenant_id, start_date, end_date, tenant_name = check_params(tenant_id, start_date, end_date)

        results = await asyncio.gather(
            get_feature_access_frequency(feature, tenant_id, start_date, end_date),
            get_feature_average_usage_duration_minutes(feature, tenant_id, start_date, end_date),
            get_feature_engagement_rate(feature, tenant_id, start_date, end_date),
            get_feature_retention_rate_on_specific_days(feature, tenant_id, start_date, end_date),
            get_feature_retention_rate_in_specific_intervals(feature, tenant_id, start_date, end_date),
            get_feature_drop_off_points(feature, tenant_id, start_date, end_date)
        )

        access_frequency = results[0]
        average_time_spent = results[1]
        engagement_rate = results[2]
        retention_rate_on_specific_days = results[3]
        retention_rate_in_specific_intervals = results[4]
        drop_off_points = results[5]

        feature_engagement_metrics = FeatureEngagementMetrics(
            Feature=feature,
            TenantId=tenant_id,
            TenantName=tenant_name,
            StartDate=str(start_date) if start_date else 'Unspecified',
            EndDate=str(end_date) if end_date else 'Unspecified',
            AccessFrequency=access_frequency,
            AverageUsageDurationMinutes=average_time_spent,
            EngagementRate=engagement_rate,
            RetentionRateOnSpecificDays=retention_rate_on_specific_days,
            RetentionRateInSpecificIntervals=retention_rate_in_specific_intervals,
            DropOffPoints=drop_off_points
        )

        return feature_engagement_metrics

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

async def generate_reports(analysis_code, metrics):
    try:
        json_file_path = await generate_user_engagement_report_json(analysis_code, metrics)
        excel_file_path = await generate_user_engagement_report_excel(analysis_code, metrics)
        pdf_file_path = await generate_user_engagement_report_pdf(analysis_code, metrics)

        print(f"JSON file path: {json_file_path}")
        print(f"Excel file path: {excel_file_path}")
        print(f"PDF file path: {pdf_file_path}")

    except Exception as e:
        print(e)

###############################################################################
