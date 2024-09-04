from datetime import date, timedelta
from typing import Optional
import asyncio

from pydantic import UUID4
from app.common.validators import validate_uuid4
from app.database.services.analytics_basics import get_all_registered_users
from app.domain_types.schemas.analytics import BasicAnalyticsStatistics, Demographics
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
            # get_all_registered_patients(tenant_id, start_date, end_date),
            # get_current_active_patients(tenant_id, start_date, end_date),
            # get_patient_registration_hisory_by_months(tenant_id, start_date, end_date),
            # get_patient_deregistration_history_by_months(tenant_id, start_date, end_date),
            # get_patient_age_demographics(tenant_id, start_date, end_date),
            # get_patient_gender_demographics(tenant_id, start_date, end_date),
            # get_patient_ethnicity_demographics(tenant_id, start_date, end_date),
            # get_patient_race_demographics(tenant_id, start_date, end_date),
            # get_patient_healthsystem_distribution(tenant_id, start_date, end_date),
            # get_patient_hospital_distribution(tenant_id, start_date, end_date),
            # get_patient_survivor_or_caregiver_distribution(tenant_id, start_date, end_date)
        )

        total_users = results[0]
        # total_patients = results[1]
        # active_patients = results[2]
        # registration_history = results[3]
        # deregistration_history = results[4]
        # age_demographics = results[5]
        # gender_demographics = results[6]
        # ethnicity_demographics = results[7]
        # race_demographics = results[8]
        # healthsystem_distribution = results[9]
        # hospital_distribution = results[10]
        # survivor_or_caregiver_distribution = results[11]

        # demographics = Demographics(
        #     AgeGroups                       = age_demographics,
        #     GenderGroups                    = gender_demographics,
        #     LocationGroups                  = {},
        #     EthnicityGroups                 = ethnicity_demographics,
        #     RaceGroups                      = race_demographics,
        #     HealthSystemDistribution        = healthsystem_distribution,
        #     HospitalDistribution            = hospital_distribution,
        #     SurvivorOrCareGiverDistribution = survivor_or_caregiver_distribution
        # )

        # stats = BasicAnalyticsStatistics(
        #     TenantId=tenant_id,
        #     TenantName=tenant_name,
        #     StartDate=start_date,
        #     EndDate=end_date,
        #     TotalUsers=total_users,
        #     TotalPatients=total_patients,
        #     TotalActivePatients=active_patients,
        #     PatientRegistrationHistory=registration_history,
        #     PatientDeregistrationHistory=deregistration_history,
        #     PatientDemographics=demographics,
        # )

        # return stats

        return None

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

def check_params(tenant_id, start_date, end_date):
    tenant_name = "default"
    if not start_date:
        start_date = date.today() - timedelta(days=PAST_DAYS_TO_CONSIDER)
    if not end_date:
        end_date = date.today()
    if not tenant_id:
        tenant = DataSynchronizer.get_tenant_by_code('default')
        if tenant is not None:
            tenant_id = tenant['id']
            tenant_name = tenant['TenantName']
    else:
        tenant = DataSynchronizer.get_tenant(tenant_id)
        if tenant is not None:
            tenant_name = tenant['TenantName']
    return tenant_id,start_date,end_date,tenant_name

