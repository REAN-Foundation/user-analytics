
import asyncio
import os
from typing import List

import pandas as pd
from app.database.services.analytics.reports.report_utilities import (
    plot_bar_chart,
    plot_pie_chart,
    reindex_dataframe_to_all_dates
)
from app.domain_types.schemas.analytics import (
    BasicAnalyticsStatistics,
    EngagementMetrics,
    FeatureEngagementMetrics,
    GenericEngagementMetrics
)

###############################################################################

def generate_report_images(
        report_folder_path: str,
        metrics: EngagementMetrics) -> bool:

    generated_stats_images = generate_basic_statistics_images(report_folder_path, metrics.BasicStatistics)
    generated_generic_metrics_images = generate_generic_engagement_images(report_folder_path, metrics.GenericMetrics)
    generated_feature_metrics_images = generate_feature_engagement_images(report_folder_path, metrics.FeatureMetrics)

    return generated_stats_images and generated_generic_metrics_images and generated_feature_metrics_images

###############################################################################

def generate_basic_statistics_images(
        location: str,
        metrics: BasicAnalyticsStatistics) -> bool:

    try:

        registration_history_df      = pd.DataFrame(metrics.PatientRegistrationHistory)
        deregistration_history_df    = pd.DataFrame(metrics.PatientDeregistrationHistory)
        age_groups_df                = pd.DataFrame(metrics.PatientDemographics.AgeGroups)
        gender_groups_df             = pd.DataFrame(metrics.PatientDemographics.GenderGroups)
        ethnicity_groups_df          = pd.DataFrame(metrics.PatientDemographics.EthnicityGroups)
        race_groups_df               = pd.DataFrame(metrics.PatientDemographics.RaceGroups)
        healthsystem_distribution_df = pd.DataFrame(metrics.PatientDemographics.HealthSystemDistribution)
        hospital_distribution_df     = pd.DataFrame(metrics.PatientDemographics.HospitalDistribution)
        caregiver_status_df          = pd.DataFrame(metrics.PatientDemographics.SurvivorOrCareGiverDistribution)

        # handling missing values
        registration_history_df_filled = reindex_dataframe_to_all_dates(
            data_frame  = registration_history_df,
            date_column = 'month',
            fill_column = 'user_count',
            frequency   = 'MS',
            date_format = '%Y-%m')

        deregistration_history_df_filled = reindex_dataframe_to_all_dates(
            data_frame  = deregistration_history_df,
            date_column = 'month',
            fill_column = 'user_count',
            frequency   = 'MS',
            date_format = '%Y-%m')

        # plot the charts

        plot_bar_chart(
            data_frame    = registration_history_df_filled,
            x_column      = 'month',
            y_column      = 'user_count',
            title         = 'Patient Registration History',
            x_label       = 'Month',
            y_label       = 'Number of Registrations',
            color_palette = 'Blues_d',
            file_path     = os.path.join(location, 'patient_registration_history'))

        plot_bar_chart(
            data_frame    = deregistration_history_df_filled,
            x_column      = 'month',
            y_column      = 'user_count',
            title         = 'Patient Deregistration History',
            x_label       = 'Month',
            y_label       = 'Number of Deregistrations',
            color_palette = 'Reds_d',
            file_path     = os.path.join(location, 'patient_deregistration_history'))

        plot_bar_chart(
            data_frame    = healthsystem_distribution_df,
            x_column      = 'health_system',
            y_column      = 'count',
            title         = 'Health System Distribution',
            x_label       = 'Health System',
            y_label       = 'Patient Count',
            color_palette = 'Greens_d',
            file_path     = os.path.join(location, 'health_system_distribution'))

        plot_bar_chart(
            data_frame    = hospital_distribution_df,
            x_column      = 'hospital',
            y_column      = 'count',
            title         = 'Hospital Distribution',
            x_label       = 'Hospital',
            y_label       = 'Patient Count',
            color_palette = 'Oranges_d',
            file_path     = os.path.join(location, 'hospital_distribution'))

        plot_pie_chart(
            data_frame    = age_groups_df,
            value_column  = 'count',
            label_column  = 'age_group',
            title         = 'Patient Age Groups',
            color_palette = 'Set3',
            file_path     = os.path.join(location, 'patient_age_groups'))

        plot_pie_chart(
            data_frame    = gender_groups_df,
            value_column  = 'count',
            label_column  = 'gender',
            title         = 'Patient Gender Groups',
            color_palette = 'Set3',
            file_path     = os.path.join(location, 'patient_gender_groups'))

        plot_pie_chart(
            data_frame    = ethnicity_groups_df,
            value_column  = 'count',
            label_column  = 'ethnicity',
            title         = 'Patient Ethnicity Groups',
            color_palette = 'Set2',
            file_path     = os.path.join(location, 'patient_ethnicity_groups'))

        plot_pie_chart(
            data_frame    = race_groups_df,
            value_column  = 'count',
            label_column  = 'race',
            title         = 'Patient Race Groups',
            color_palette = 'Set2',
            file_path     = os.path.join(location, 'patient_race_groups'))

        plot_pie_chart(
            data_frame    = caregiver_status_df,
            value_column  = 'count',
            label_column  = 'caregiver_status',
            title         = 'Survivor or Caregiver Distribution',
            color_palette = 'Set1',
            file_path     = os.path.join(location, 'survivor_caregiver_distribution'))

    except Exception as e:
        print(f"Error generating basic statistics images: {e}")
        return False

    return True

###############################################################################

def generate_generic_engagement_images(
        location: str,
        metrics: GenericEngagementMetrics) -> bool:

    daily_active_users_df    = pd.DataFrame(metrics.DailyActiveUsers)
    weekly_active_users_df   = pd.DataFrame(metrics.WeeklyActiveUsers)
    monthly_active_users_df  = pd.DataFrame(metrics.MonthlyActiveUsers)
    login_frequency_df       = pd.DataFrame(metrics.LoginFrequency)
    retention_on_days_df     = pd.DataFrame(metrics.RetentionRateOnSpecificDays['retention_on_specific_days'])
    retention_intervals_df   = pd.DataFrame(metrics.RetentionRateInSpecificIntervals['retention_in_specific_interval'])
    most_visited_features_df = pd.DataFrame(metrics.MostCommonlyVisitedFeatures)

    # missing dates, weeks, and months
    daily_active_users_df_filled   = reindex_dataframe_to_all_dates(
        data_frame  = daily_active_users_df,
        date_column = 'activity_date',
        fill_column = 'daily_active_users',
        frequency   = 'D',
        date_format = '%Y-%m-%d')

    monthly_active_users_df_filled = reindex_dataframe_to_all_dates(
        data_frame  = monthly_active_users_df,
        date_column = 'activity_month',
        fill_column = 'monthly_active_users',
        frequency   = 'MS',
        date_format = '%Y-%m')

    plot_bar_chart(
        data_frame     = daily_active_users_df_filled,
        x_column       = 'activity_date',
        y_column       = 'daily_active_users',
        title          = 'Daily Active Users',
        x_label        = 'Date',
        y_label        = 'Number of Active Users',
        color_palette  = 'Blues_d',
        file_path      = os.path.join(location, 'daily_active_users'),
        rotation       = 45,
        show_every_nth = 10)

    plot_bar_chart(
        data_frame    = weekly_active_users_df,
        x_column      = 'week_start_date',
        y_column      = 'weekly_active_users',
        title         = 'Weekly Active Users',
        x_label       = 'Week Start Date',
        y_label       = 'Number of Active Users',
        color_palette = 'Reds_d',
        file_path     = os.path.join(location, 'weekly_active_users'))

    plot_bar_chart(
        data_frame    = monthly_active_users_df_filled,
        x_column      = 'activity_month',
        y_column      = 'monthly_active_users',
        title         = 'Monthly Active Users',
        x_label       = 'Month',
        y_label       = 'Number of Active Users',
        color_palette = 'Greens_d',
        file_path     = os.path.join(location, 'monthly_active_users'))

    plot_bar_chart(
        data_frame    = login_frequency_df,
        x_column      = 'month',
        y_column      = 'login_count',
        title         = 'Login Frequency by Month',
        x_label       = 'Month',
        y_label       = 'Login Count',
        color_palette = 'cubehelix',
        file_path     = os.path.join(location, 'login_frequency'))

    plot_pie_chart(
        data_frame    = retention_on_days_df,
        value_column  = 'retention_rate',
        label_column  = 'day',
        title         = 'Retention on Specific Days',
        color_palette = 'coolwarm',
        file_path     = os.path.join(location, 'retention_on_specific_days'))

    plot_pie_chart(
        data_frame    = retention_intervals_df,
        value_column  = 'retention_rate',
        label_column  = 'interval',
        title         = 'Retention in Specific Intervals',
        color_palette = 'coolwarm',
        file_path     = os.path.join(location, 'retention_in_specific_intervals'))

    return True

###############################################################################

def generate_feature_engagement_images(
        report_folder_path: str,
        feature_engagements: List[FeatureEngagementMetrics]|None) -> bool:
    features = feature_engagements.Features
    for feature in features:
        generate_feature_engagement_images(report_folder_path, feature)

def generate_feature_engagement_images(
        location: str,
        feature: FeatureEngagementMetrics) -> bool:

    feature = feature.Feature

    access_frequency_df    = pd.DataFrame(feature.AccessFrequency)
    engagement_rate_df     = pd.DataFrame(feature.EngagementRate)
    retention_on_days_df   = pd.DataFrame(feature.RetentionRateOnSpecificDays.retention_on_specific_days)  # 'day' column is fine as-is
    retention_intervals_df = pd.DataFrame(feature.RetentionRateInSpecificIntervals.retention_in_specific_interval)
    drop_off_points_df     = pd.DataFrame(feature.DropOffPoints)

    # Handle missing months for access and engagement rate
    access_frequency_df = reindex_dataframe_to_all_dates(
       data_frame  = access_frequency_df,
       date_column = 'month',
       fill_column = 'access_frequency',
       frequency   = 'MS',
       date_format = '%Y-%m')

    engagement_rate_df = reindex_dataframe_to_all_dates(
        data_frame  = engagement_rate_df,
        date_column = 'month',
        fill_column = 'engagement_rate',
        frequency   = 'MS',
        date_format = '%Y-%m')

    engagement_rate_df['engagement_rate'] = engagement_rate_df['engagement_rate'].astype(float)

    plot_bar_chart(
        data_frame    = access_frequency_df,
        x_column      = 'month',
        y_column      = 'access_frequency',
        title         = 'Access Frequency by Month',
        x_label       = 'Month',
        y_label       = 'Access Frequency',
        color_palette = 'Blues_d',
        file_path     = os.path.join(location, f'{feature}_access_frequency_by_month'))

    plot_bar_chart(
        data_frame    = engagement_rate_df,
        x_column      = 'month',
        y_column      = 'engagement_rate',
        title         = 'Engagement Rate by Month',
        x_label       = 'Month',
        y_label       = 'Engagement Rate (%)',
        color_palette = 'Greens_d',
        file_path     = os.path.join(location, f'{feature}_engagement_rate_by_month'))

    plot_pie_chart(
        data_frame    = retention_on_days_df,
        value_column  = 'retention_rate',
        label_column  = 'day',
        title         = 'Retention on Specific Days',
        color_palette = 'Set3',
        file_path     = os.path.join(location, f'{feature}_retention_on_specific_days'))

    plot_bar_chart(
        data_frame    = retention_intervals_df,
        x_column      = 'interval',
        y_column      = 'retention_rate',
        title         = 'Retention Rate in Specific Intervals',
        x_label       = 'Interval',
        y_label       = 'Retention Rate (%)',
        color_palette = 'Purples_d',
        file_path     = os.path.join(location, f'{feature}_retention_in_specific_intervals'))

    plot_pie_chart(
        data_frame    = drop_off_points_df,
        value_column  = 'dropoff_rate',
        label_column  = 'event_name',
        title         = 'Drop-Off Points by Event',
        color_palette = 'Set2',
        file_path     = os.path.join(location, f'{feature}_drop_off_points'))

    return True

###############################################################################
