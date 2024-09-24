from datetime import date, timedelta
import asyncio
import os

from pydantic import UUID4

from app.common.utils import print_exception
from app.database.database_accessor import get_db_session
from app.database.models.analysis import Analysis
from app.database.models.tenant import Tenant
from app.database.services.analytics.basic_statistics import (
    get_active_users_count_at_end_of_every_month,
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
    get_patient_survivor_or_caregiver_distribution,
    get_users_distribution_by_role
)
from app.database.services.analytics.common import get_role_id
from app.database.services.analytics.generic_engagement import (
    get_daily_active_patients,
    get_monthly_active_patients,
    get_most_fired_events_by_event_category,
    get_patient_stickiness_dau_mau,
    get_patients_average_session_length_in_minutes,
    get_patients_login_frequency,
    get_patients_most_commonly_used_features,
    get_patients_most_commonly_visited_screens,
    get_patients_retention_rate_in_specific_time_interval,
    get_patients_retention_rate_on_specific_days,
    get_weekly_active_patients,
    get_most_fired_events
)
from app.database.services.analytics.feature_engagement import (
    get_feature_access_frequency,
    get_feature_engagement_rate,
    get_feature_retention_rate_on_specific_days,
    get_feature_retention_rate_in_specific_intervals,
    get_feature_average_usage_duration_minutes,
    get_feature_drop_off_points,
)
from app.database.services.analytics.reports.report_generator_excel import generate_report_excel
from app.database.services.analytics.reports.report_generator_json import generate_report_json
from app.database.services.analytics.reports.report_generator_pdf import generate_report_pdf
from app.domain_types.enums.event_categories import EventCategory
from app.domain_types.schemas.analytics import (
    AnalyticsFilters,
    BasicAnalyticsStatistics,
    Demographics,
    FeatureEngagementMetrics,
    EngagementMetrics,
    GenericEngagementMetrics
)
from app.modules.data_sync.connectors import get_analytics_db_connector
from app.modules.data_sync.data_synchronizer import DataSynchronizer

###############################################################################
PAST_DAYS_TO_CONSIDER = 900
###############################################################################

async def calculate(
        analysis_code: str, filters: AnalyticsFilters|None) -> EngagementMetrics|None:

    print(f"Analysis started -> {analysis_code} -> filters -> {str(filters)}")

    try:
        basic_stats = await calculate_basic_stats(filters)
        print("Calculated basic stats")

        generic_metrics = await calculate_generic_engagement_metrics(filters)
        print("Calculated generic metrics")

        features = [
            EventCategory.LoginSession,
            EventCategory.Medication,
            EventCategory.Symptoms,
            EventCategory.Vitals,
            EventCategory.Careplan,
            EventCategory.UserTask,
        ]
        metrics_by_feature = []
        for feature in features:
            engament = await calculate_feature_engagement_metrics(feature, filters)
            print(f"Calculated metrics for {feature}")
            metrics_by_feature.append(engament)

        metrics = EngagementMetrics(
            TenantId        = filters.TenantId,
            TenantName      = filters.TenantName if filters.TenantName != None else 'Unspecified',
            StartDate       = str(filters.StartDate) if filters.StartDate else 'Unspecified',
            EndDate         = str(filters.EndDate) if filters.EndDate else 'Unspecified',
            BasicStatistics = basic_stats,
            GenericMetrics  = generic_metrics,
            FeatureMetrics  = metrics_by_feature
        )

        saved_analytics = await save_analytics(analysis_code, metrics)
        print(f"Saved analytics -> {analysis_code}")

        await generate_reports(analysis_code, metrics)
        print(f"Generated reports -> {analysis_code}")

        return metrics

    except Exception as e:
        print_exception(e)

###############################################################################

async def calculate_basic_stats(filters: AnalyticsFilters | None = None) -> BasicAnalyticsStatistics|None:
    try:

        filters = check_filter_params(filters)

        results = await asyncio.gather(
            get_all_registered_users(filters),
            get_all_registered_patients(filters),
            get_current_active_patients(filters),
            get_patient_registration_hisory_by_months(filters),
            get_patient_deregistration_history_by_months(filters),
            get_patient_age_demographics(filters),
            get_patient_gender_demographics(filters),
            get_patient_ethnicity_demographics(filters),
            get_patient_race_demographics(filters),
            get_patient_healthsystem_distribution(filters),
            get_patient_hospital_distribution(filters),
            get_patient_survivor_or_caregiver_distribution(filters),
            get_users_distribution_by_role(filters),
            get_active_users_count_at_end_of_every_month(filters)
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
        users_distribution_by_role         = results[12]
        active_users_count_at_end_of_every_month = results[13]

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
            TenantId                     = filters.TenantId,
            TenantName                   = filters.TenantName,
            StartDate                    = str(filters.StartDate) if filters.StartDate else 'Unspecified',
            EndDate                      = str(filters.EndDate) if filters.EndDate else 'Unspecified',
            TotalUsers                   = total_users,
            TotalPatients                = total_patients,
            TotalActivePatients          = active_patients,
            UsersDistributionByRole      = users_distribution_by_role,
            ActiveUsersCountAtEndOfMonth = active_users_count_at_end_of_every_month,
            PatientRegistrationHistory   = registration_history,
            PatientDeregistrationHistory = deregistration_history,
            PatientDemographics          = demographics,
        )

        return stats

    except Exception as e:
        print_exception(e)

async def calculate_generic_engagement_metrics(filters: AnalyticsFilters | None = None) -> GenericEngagementMetrics|None:
    try:
        filters = check_filter_params(filters)

        results = await asyncio.gather(
                get_daily_active_patients(filters),
                get_weekly_active_patients(filters),
                get_monthly_active_patients(filters),
                get_patients_average_session_length_in_minutes(filters),
                get_patients_login_frequency(filters),
                get_patients_retention_rate_on_specific_days(filters),
                get_patients_retention_rate_in_specific_time_interval(filters),
                get_patient_stickiness_dau_mau(filters),
                get_patients_most_commonly_used_features(filters),
                get_patients_most_commonly_visited_screens(filters),
                get_most_fired_events(filters),
                get_most_fired_events_by_event_category(filters)
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
        most_fired_events                   = results[10]
        most_fired_events_by_event_category = results[11]

        generic_engagement_metrics = GenericEngagementMetrics(
                TenantId                         = filters.TenantId,
                TenantName                       = filters.TenantName,
                StartDate                        = str(filters.StartDate) if filters.StartDate else 'Unspecified',
                EndDate                          = str(filters.EndDate) if filters.EndDate else 'Unspecified',
                DailyActiveUsers                 = daily_active_users,
                WeeklyActiveUsers                = weekly_active_users,
                MonthlyActiveUsers               = monthly_active_users,
                AverageSessionLengthMinutes      = average_session_length if average_session_length else 0,
                LoginFrequency                   = login_frequency,
                RetentionRateOnSpecificDays      = retention_rate_on_specific_days,
                RetentionRateInSpecificIntervals = retention_rate_in_specific_intervals,
                StickinessRatio                  = stickiness_ratio,
                MostCommonlyVisitedFeatures      = most_common_features,
                MostCommonlyVisitedScreens       = most_commonly_visited_screens,
                MostFiredEvents                  = most_fired_events,
                MostFiredEventsByEventCategory   = most_fired_events_by_event_category
            )

        return generic_engagement_metrics

    except Exception as e:
        print_exception(e)

async def calculate_feature_engagement_metrics(
        feature: str, filters: AnalyticsFilters | None = None)-> FeatureEngagementMetrics|None:
    try:
        filters = check_filter_params(filters)

        results = await asyncio.gather(
            get_feature_access_frequency(feature, filters),
            get_feature_average_usage_duration_minutes(feature, filters),
            get_feature_engagement_rate(feature, filters),
            get_feature_retention_rate_on_specific_days(feature, filters),
            get_feature_retention_rate_in_specific_intervals(feature, filters),
            get_feature_drop_off_points(feature, filters)
        )

        access_frequency = results[0]
        average_time_spent = results[1]
        engagement_rate = results[2]
        retention_rate_on_specific_days = results[3]
        retention_rate_in_specific_intervals = results[4]
        drop_off_points = results[5]

        feature_engagement_metrics = FeatureEngagementMetrics(
            Feature                          = feature,
            TenantId                         = filters.TenantId,
            TenantName                       = filters.TenantName,
            StartDate                        = str(filters.StartDate) if filters.StartDate else 'Unspecified',
            EndDate                          = str(filters.EndDate) if filters.EndDate else 'Unspecified',
            AccessFrequency                  = access_frequency,
            AverageUsageDurationMinutes      = average_time_spent,
            EngagementRate                   = engagement_rate,
            RetentionRateOnSpecificDays      = retention_rate_on_specific_days,
            RetentionRateInSpecificIntervals = retention_rate_in_specific_intervals,
            DropOffPoints                    = drop_off_points
        )

        return feature_engagement_metrics

    except Exception as e:
        print_exception(e)

###############################################################################

def check_filter_params(filters: AnalyticsFilters | None = None) -> AnalyticsFilters:

    tenant_name = "unspecified"
    start_date = date.today() - timedelta(days=PAST_DAYS_TO_CONSIDER)
    end_date = date.today()
    role_id = get_role_id() # This defaults to 'Patient' role

    if filters is None:
        return AnalyticsFilters(
            TenantId=None,
            TenantName=tenant_name,
            RoleId=role_id,
            StartDate=start_date,
            EndDate=end_date,
            Source=None,
            )

    if not filters.RoleId or filters.RoleId < 0 or filters.RoleId > 20:
        filters.RoleId = role_id

    if not filters.StartDate:
        filters.StartDate = start_date
    if not filters.EndDate:
        filters.EndDate = end_date

    if not filters.TenantId:
        return AnalyticsFilters(
            TenantId=None,
            TenantName=tenant_name,
            RoleId=filters.RoleId,
            StartDate=filters.StartDate,
            EndDate=filters.EndDate,
            Source=filters.Source,
            )
    else:
        tenant = DataSynchronizer.get_tenant(filters.TenantId)
        if tenant is not None:
            filters.TenantName = tenant['TenantName']

    return filters

async def generate_reports(analysis_code: str, metrics: EngagementMetrics):
    try:
        json_file_path = await generate_report_json(analysis_code, metrics)
        excel_file_path = await generate_report_excel(analysis_code, metrics)
        pdf_file_path = await generate_report_pdf(analysis_code, metrics)

        print(f"JSON file path: {json_file_path}")
        print(f"Excel file path: {excel_file_path}")
        print(f"PDF file path: {pdf_file_path}")

    except Exception as e:
        print_exception(e)

###############################################################################

async def get_analysis_code():
    today = date.today().strftime("%Y-%m-%d")
    existing_count = 0
    try:
        session = get_db_session()
        existing = session.query(Analysis).filter(Analysis.Code.startswith(today)).all()
        if existing is not None and len(existing) > 0:
            existing_count = len(existing)
        session.close()
    except Exception as e:
        print_exception(e)

    existing_count += 1
    return f"{today}-{existing_count}"

async def get_tenant_by_id(tenantId: UUID4 | None):
    tenant = None
    try:
        session = get_db_session()
        tenant = await session.query(Tenant).filter(Tenant.id == tenantId).first()
    except Exception as e:
        print_exception(e)
    finally:
        session.close()
    return tenant

async def get_all_tenants():
    analytics_db_connector = get_analytics_db_connector()
    query = f"""
    SELECT * from tenants
    """
    rows = analytics_db_connector.execute_read_query(query)
    return rows
###############################################################################

async def save_analytics(analysis_code: str, metrics: EngagementMetrics)-> dict:

    print(f"Saving analytics -> {analysis_code}")
    session = get_db_session()
    base_url = os.getenv("BASE_URL")

    try:
        db_model = Analysis(
            Code       = analysis_code,
            TenantId   = str(metrics.TenantId),
            TenantName = metrics.TenantName,
            DateStr    = date.today().strftime("%Y-%m-%d"),
            Data       = str(metrics.model_dump_json()),
            StartDate  = metrics.StartDate,
            EndDate    = metrics.EndDate,
            JsonUrl    = f"{base_url}/api/v1/analytics/download/{analysis_code}/formats/json",
            ExcelUrl   = f"{base_url}/api/v1/analytics/download/{analysis_code}/formats/excel",
            PdfUrl     = f"{base_url}/api/v1/analytics/download/{analysis_code}/formats/pdf",
            Url        = f"{base_url}/api/v1/analytics/metrics/{analysis_code}",
            CreatedAt  = date.today(),
            UpdatedAt  = date.today()
        )

        session.add(db_model)
        session.commit()
        temp = session.refresh(db_model)
        analysis = db_model
        return analysis.__dict__

    except Exception as e:
        session.rollback()
        session.close()
        raise e
    finally:
        session.close()

###############################################################################

async def get_analysis_by_code(analysis_code: str)-> dict:
    try:
        session = get_db_session()
        analysis = session.query(Analysis).filter(Analysis.Code == analysis_code).first()
        if analysis is None:
            raise Exception(f"Analysis with code {analysis_code} not found")
        session.close()
        # return analysis.__dict__
        return analysis
    except Exception as e:
        print_exception(e)

###############################################################################

async def generate_daily_analytics():
    try:
        session = get_db_session()

        tenants = []
        tenants_ = await get_all_tenants()
        for tenant in tenants_:
            tenants.append({
                "TenantId": tenant['id'],
                "TenantCode": tenant['TenantCode'],
            })
        # Also add analysis ignoring the tenant filter
        tenants.append({
            "TenantId": None,
            "TenantCode": None,
        })

        for tenant in tenants:
            filters = AnalyticsFilters(
                TenantId = tenant['TenantId'],
                TenantName = tenant['TenantCode'],
                RoleId = get_role_id(),
                StartDate = date.today() - timedelta(days=PAST_DAYS_TO_CONSIDER),
                EndDate = date.today(),
                Source = None
            )
            analysis_code = await get_analysis_code()
            if tenant['TenantCode'] is not None:
                analysis_code = analysis_code + '_' + tenant['TenantCode']
            metrics = await calculate(analysis_code, filters)

    except Exception as e:
        print_exception(e)
    finally:
        session.close()
