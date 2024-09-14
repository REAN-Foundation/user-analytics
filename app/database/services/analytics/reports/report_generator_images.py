
import asyncio
from typing import List

import pandas as pd
from app.database.services.analytics.reports.report_utilities import plot_bar_chart, plot_pie_chart, reindex_dataframe_to_all_dates
from app.domain_types.schemas.analytics import (
    BasicAnalyticsStatistics,
    EngagementMetrics,
    FeatureEngagementMetrics,
    GenericEngagementMetrics
)

###############################################################################

async def generate_user_engagement_report_images(
        report_folder_path: str,
        user_engagement_metrics: EngagementMetrics) -> bool:

    results = await asyncio.gather(
        generate_basic_statistics_images(report_folder_path, user_engagement_metrics.BasicStatistics),
        generate_generic_engagement_images(report_folder_path, user_engagement_metrics.GenericEngagement),
        generate_feature_engagement_images(report_folder_path, user_engagement_metrics.FeatureEngagement)
    )

    return True

async def generate_basic_statistics_images(
        report_folder_path: str,
        basic_statistics: BasicAnalyticsStatistics) -> bool:

    registration_history_df = pd.DataFrame(basic_statistics['PatientRegistrationHistory'])
    deregistration_history_df = pd.DataFrame(basic_statistics['PatientDeregistrationHistory'])
    age_groups_df = pd.DataFrame(basic_statistics['PatientDemographics']['AgeGroups'])
    gender_groups_df = pd.DataFrame(basic_statistics['PatientDemographics']['GenderGroups'])
    ethnicity_groups_df = pd.DataFrame(basic_statistics['PatientDemographics']['EthnicityGroups'])
    race_groups_df = pd.DataFrame(basic_statistics['PatientDemographics']['RaceGroups'])
    healthsystem_distribution_df = pd.DataFrame(basic_statistics['PatientDemographics']['HealthSystemDistribution'])
    hospital_distribution_df = pd.DataFrame(basic_statistics['PatientDemographics']['HospitalDistribution'])
    caregiver_status_df = pd.DataFrame(basic_statistics['PatientDemographics']['SurvivorOrCareGiverDistribution'])

    # handling missing values
    registration_history_df_filled = reindex_dataframe_to_all_dates(registration_history_df, 'month', 'user_count', 'MS', '%Y-%m')
    deregistration_history_df_filled = reindex_dataframe_to_all_dates(deregistration_history_df, 'month', 'user_count', 'MS', '%Y-%m')

    # plotting bar graphs
    plot_bar_chart(registration_history_df_filled, 'month', 'user_count', 'Patient Registration History', 'Month', 'Number of Registrations', 'Blues_d', 'Patient_Registration_History')
    plot_bar_chart(deregistration_history_df_filled, 'month', 'user_count', 'Patient Deregistration History', 'Month', 'Number of Deregistrations', 'Reds_d', 'Patient_Deregistration_History')
    plot_bar_chart(healthsystem_distribution_df, 'healthsystem', 'count', 'Health System Distribution', 'Health System', 'Patient Count', 'Greens_d', 'Health_System_Distribution')
    plot_bar_chart(hospital_distribution_df, 'hospital', 'count', 'Hospital Distribution', 'Hospital', 'Patient Count', 'Oranges_d', 'Hospital_Distribution')

    # plotting pie charts
    plot_pie_chart(age_groups_df, 'count', 'age_group', 'Patient Age Groups', 'Set3', 'Patient_Age_Groups')
    plot_pie_chart(gender_groups_df, 'count', 'gender', 'Patient Gender Groups', 'Set3', 'Patient_Gender_Groups')
    plot_pie_chart(ethnicity_groups_df, 'count', 'ethnicity', 'Patient Ethnicity Groups', 'Set2', 'Patient_Ethnicity_Groups')
    plot_pie_chart(race_groups_df, 'count', 'race', 'Patient Race Groups', 'Set2', 'Patient_Race_Groups')
    plot_pie_chart(caregiver_status_df, 'count', 'caregiver_status', 'Survivor or Caregiver Distribution', 'Set1', 'Survivor_Caregiver_Distribution')

    return True

async def generate_generic_engagement_images(
        report_folder_path: str,
        generic_engagement: GenericEngagementMetrics) -> bool:
    return True

async def generate_feature_engagement_images(
        report_folder_path: str,
        feature_engagements: List[FeatureEngagementMetrics]|None) -> bool:
    features = feature_engagements.Features
    for feature in features:
        await generate_feature_engagement_images(report_folder_path, feature)

async def generate_feature_engagement_images(
        report_folder_path: str,
        feature: FeatureEngagementMetrics) -> bool:
    return True

###############################################################################
