
import os
from typing import List
import pandas as pd
from app.database.services.analytics.reports.report_utilities import (
    plot_area_graph,
    plot_bar_chart,
    plot_pie_chart,
    reindex_dataframe_to_all_dates,
    format_date_column,
    reindex_dataframe_to_all_missing_dates
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
    generated_feature_metrics_images = generate_feature_engagement_images(report_folder_path, metrics.FeatureMetrics, metrics.MedicationManagementMetrics)

    return generated_stats_images or generated_generic_metrics_images or generated_feature_metrics_images

###############################################################################

def generate_basic_statistics_images(
        location: str,
        metrics: BasicAnalyticsStatistics) -> bool:

    try:
        registration_history_df             = pd.DataFrame(metrics.PatientRegistrationHistory)
        deregistration_history_df           = pd.DataFrame(metrics.PatientDeregistrationHistory)
        age_groups_df                       = pd.DataFrame(metrics.PatientDemographics.AgeGroups)
        gender_groups_df                    = pd.DataFrame(metrics.PatientDemographics.GenderGroups)
        ethnicity_groups_df                 = pd.DataFrame(metrics.PatientDemographics.EthnicityGroups)
        race_groups_df                      = pd.DataFrame(metrics.PatientDemographics.RaceGroups)
        healthsystem_distribution_df        = pd.DataFrame(metrics.PatientDemographics.HealthSystemDistribution)
        hospital_distribution_df            = pd.DataFrame(metrics.PatientDemographics.HospitalDistribution)
        caregiver_status_df                 = pd.DataFrame(metrics.PatientDemographics.SurvivorOrCareGiverDistribution)
        user_distribution_by_role_df        = pd.DataFrame(metrics.UsersDistributionByRole)
        active_users_count_at_end_of_month  = pd.DataFrame(metrics.ActiveUsersCountAtEndOfMonth)

        if not registration_history_df.empty:
            registration_history_df  = pd.DataFrame(metrics.PatientRegistrationHistory) 
            registration_history_df_filled = reindex_dataframe_to_all_missing_dates(
                data_frame = registration_history_df,
                date_col = 'month',
                fill_col = 'user_count',
            )
            registration_history_df_filled_ = format_date_column(registration_history_df_filled, 'month')
            
            plot_bar_chart(
                data_frame    = registration_history_df_filled_,
                x_column      = 'month',
                y_column      = 'user_count',
                title         = 'Registration History',
                x_label       = 'Month',
                y_label       = 'Number of Registrations',
                color_palette = 'Blues_d',
                file_path     = os.path.join(location, 'registration_history'))

        if not deregistration_history_df.empty:
            deregistration_history_df_filled = reindex_dataframe_to_all_missing_dates(
                data_frame = deregistration_history_df,
                date_col = 'month',
                fill_col = 'user_count',
            )
            deregistration_history_df_filled_ = format_date_column(deregistration_history_df_filled, 'month')

            plot_bar_chart(
                data_frame    = deregistration_history_df_filled_,
                x_column      = 'month',
                y_column      = 'user_count',
                title         = 'Deregistration History',
                x_label       = 'Month',
                y_label       = 'Number of Deregistrations',
                color_palette = 'Reds_d',
                file_path     = os.path.join(location, 'deregistration_history'))

        if not healthsystem_distribution_df.empty:
            plot_pie_chart(
                data_frame    = healthsystem_distribution_df,
                value_column  = 'count',
                label_column  = 'health_system',
                title         = 'Health System Distribution',
                color_palette = 'Set3',
                file_path     = os.path.join(location, 'health_system_distribution'))

        if not healthsystem_distribution_df.empty:
            plot_pie_chart(
                data_frame    = hospital_distribution_df,
                value_column  = 'count',
                label_column  = 'hospital',
                title         = 'Hospital Distribution',
                color_palette = 'Set3',
                file_path     = os.path.join(location, 'hospital_distribution'))

        if not age_groups_df.empty:
            plot_pie_chart(
                data_frame    = age_groups_df,
                value_column  = 'count',
                label_column  = 'age_group',
                title         = 'Patient Age Distribution',
                color_palette = 'Set3',
                file_path     = os.path.join(location, 'age_distribution'))

        if not gender_groups_df.empty:
            plot_pie_chart(
                data_frame    = gender_groups_df,
                value_column  = 'count',
                label_column  = 'gender',
                title         = 'Patient Gender Groups',
                color_palette = 'Set3',
                file_path     = os.path.join(location, 'patient_gender_groups'))

        if not ethnicity_groups_df.empty:
            plot_pie_chart(
                data_frame    = ethnicity_groups_df,
                value_column  = 'count',
                label_column  = 'ethnicity',
                title         = 'Patient Ethnicity Groups',
                color_palette = 'Set2',
                file_path     = os.path.join(location, 'patient_ethnicity_groups'))

        if not race_groups_df.empty:
            plot_pie_chart(
                data_frame    = race_groups_df,
                value_column  = 'count',
                label_column  = 'race',
                title         = 'Patient Race Groups',
                color_palette = 'Set2',
                file_path     = os.path.join(location, 'patient_race_groups'))

        if not caregiver_status_df.empty:
            plot_pie_chart(
                data_frame    = caregiver_status_df,
                value_column  = 'count',
                label_column  = 'caregiver_status',
                title         = 'Survivor or Caregiver Distribution',
                color_palette = 'Set1',
                file_path     = os.path.join(location, 'survivor_caregiver_distribution'))

        if not user_distribution_by_role_df.empty:
            plot_pie_chart(
                data_frame    = user_distribution_by_role_df,
                value_column  = 'registration_count',
                label_column  = 'role_name',
                title         = 'User Distribution By Role',
                color_palette = 'Set2',
                file_path     = os.path.join(location, 'user_distribution_by_role'))
        
        if not active_users_count_at_end_of_month.empty:
            active_users_count_at_EndOfMonth_= format_date_column(active_users_count_at_end_of_month,'month_end')
            plot_area_graph(
                data_frame  = active_users_count_at_EndOfMonth_,
                x_column    = 'month_end',
                y_column    = 'active_user_count',
                title       = 'Active Users Count at End of Month',
                xlabel      = 'Month',
                ylabel      = 'Active Users',
                file_path   = os.path.join(location,'active_users_count_at_end_of_month'))
            
    except Exception as e:
        print(f"Error generating basic statistics images: {e}")
        return False

    return True

###############################################################################

def generate_generic_engagement_images(
        location: str,
        metrics: GenericEngagementMetrics) -> bool:

    try:
        daily_active_users_df    = pd.DataFrame(metrics.DailyActiveUsers)
        weekly_active_users_df   = pd.DataFrame(metrics.WeeklyActiveUsers)
        monthly_active_users_df  = pd.DataFrame(metrics.MonthlyActiveUsers)
        login_frequency_df       = pd.DataFrame(metrics.LoginFrequency)
        retention_on_days_df     = pd.DataFrame(metrics.RetentionRateOnSpecificDays['retention_on_specific_days'])
        retention_intervals_df   = pd.DataFrame(metrics.RetentionRateInSpecificIntervals['retention_in_specific_interval'])
        most_visited_features_df = pd.DataFrame(metrics.MostCommonlyVisitedFeatures)

        if not daily_active_users_df.empty:
            daily_active_users_df_filled = reindex_dataframe_to_all_missing_dates(
                data_frame = daily_active_users_df,
                date_col = 'activity_date',
                fill_col = 'daily_active_users',
                frequency = 'daily'
            )
            
            daily_active_users_df_filled_ = format_date_column(
                df          = daily_active_users_df_filled,
                column_name = 'activity_date')

            plot_bar_chart(
                data_frame     = daily_active_users_df_filled_,
                x_column       = 'activity_date',
                y_column       = 'daily_active_users',
                title          = 'Daily Active Users',
                x_label        = 'Date',
                y_label        = 'Number of Active Users',
                color_palette  = 'Blues_d',
                file_path      = os.path.join(location, 'daily_active_users'),
                rotation       = 45,
                show_every_nth = 10)

        if not weekly_active_users_df.empty:
            weekly_active_users_df = reindex_dataframe_to_all_missing_dates(
                data_frame      = weekly_active_users_df,
                start_date_col  = 'week_start_date',
                end_date_col    = 'week_end_date',
                fill_col        = 'weekly_active_users',
                frequency       = 'weekly')
            
            weekly_active_users_df_ = format_date_column(
                df          = weekly_active_users_df,
                column_name = 'week_start_date')
            
            plot_bar_chart(
                data_frame    = weekly_active_users_df_,
                x_column      = 'week_start_date',
                y_column      = 'weekly_active_users',
                title         = 'Weekly Active Users',
                x_label       = 'Week Start Date',
                y_label       = 'Number of Active Users',
                color_palette = 'Reds_d',
                file_path     = os.path.join(location, 'weekly_active_users'))

        if not weekly_active_users_df.empty:
            monthly_active_users_df_filled = reindex_dataframe_to_all_missing_dates(
                data_frame = monthly_active_users_df,
                date_col = 'activity_month',
                fill_col = 'monthly_active_users',
            )
            
            monthly_active_users_df_filled_ = format_date_column(
                df           = monthly_active_users_df_filled,
                column_name  = 'activity_month')
            
            plot_bar_chart(
                data_frame    = monthly_active_users_df_filled_,
                x_column      = 'activity_month',
                y_column      = 'monthly_active_users',
                title         = 'Monthly Active Users',
                x_label       = 'Month',
                y_label       = 'Number of Active Users',
                color_palette = 'Greens_d',
                file_path     = os.path.join(location, 'monthly_active_users'))

        if not login_frequency_df.empty:
            login_frequency_df_ = format_date_column(login_frequency_df, 'month')
            plot_bar_chart(
                data_frame    = login_frequency_df_,
                x_column      = 'month',
                y_column      = 'login_count',
                title         = 'Login Frequency by Month',
                x_label       = 'Month',
                y_label       = 'Login Count',
                color_palette = 'cubehelix',
                file_path     = os.path.join(location, 'login_frequency'))

        if not retention_on_days_df.empty:
            plot_bar_chart(
                data_frame    = retention_on_days_df,
                x_column      = 'day',
                y_column      = 'retention_rate',
                title         = 'Retention on Specific Days',
                x_label       = 'Day',
                y_label       = 'Retention',
                color_palette = 'cubehelix',
                file_path     = os.path.join(location, 'retention_on_specific_days'))

        if not retention_intervals_df.empty:
            plot_bar_chart(
                data_frame    = retention_intervals_df,
                x_column      = 'interval',
                y_column      = 'retention_rate',
                title         = 'Retention Rate in Specific Intervals',
                x_label       = 'Interval',
                y_label       = 'Retention',
                color_palette = 'cubehelix',
                file_path     = os.path.join(location, 'retention_in_specific_intervals'))

    except Exception as e:
        print(f"Error generating generic engagement images: {e}")
        return False

    return True
###############################################################################

def generate_feature_engagement_images(
        report_folder_path: str,
        feature_engagements: List[FeatureEngagementMetrics]|None,
        medication_management_metrics) -> bool:
    for fe in feature_engagements:
        feature_metrics_images(report_folder_path, fe, medication_management_metrics=medication_management_metrics)

def feature_metrics_images(
        location: str,
        feature: FeatureEngagementMetrics,
        medication_management_metrics) -> bool:

    try:

        featureName = feature.Feature

        if len(feature.AccessFrequency) > 0:
            access_frequency_df    = pd.DataFrame(feature.AccessFrequency)

            access_frequency_df = reindex_dataframe_to_all_dates(
            data_frame  = access_frequency_df,
            date_column = 'month',
            fill_column = 'access_frequency',
            frequency   = 'MS',
            date_format = '%Y-%m')

            access_frequency_df_ = format_date_column(access_frequency_df,'month')

            plot_bar_chart(
                data_frame    = access_frequency_df_,
                x_column      = 'month',
                y_column      = 'access_frequency',
                title         = 'Access Frequency by Month',
                x_label       = 'Month',
                y_label       = 'Access Frequency',
                color_palette = 'Blues_d',
                file_path     = os.path.join(location, f'{featureName}_access_frequency_by_month'))

        if len(feature.EngagementRate) > 0:

            engagement_rate_df     = pd.DataFrame(feature.EngagementRate)

            engagement_rate_df = reindex_dataframe_to_all_dates(
                data_frame  = engagement_rate_df,
                date_column = 'month',
                fill_column = 'engagement_rate',
                frequency   = 'MS',
                date_format = '%Y-%m')

            engagement_rate_df['engagement_rate'] = engagement_rate_df['engagement_rate'].astype(float)
            engagement_rate_df_ = format_date_column(engagement_rate_df,'month')

            plot_bar_chart(
                data_frame    = engagement_rate_df_,
                x_column      = 'month',
                y_column      = 'engagement_rate',
                title         = 'Engagement Rate by Month',
                x_label       = 'Month',
                y_label       = 'Engagement Rate (%)',
                color_palette = 'Greens_d',
                file_path     = os.path.join(location, f'{featureName}_engagement_rate_by_month'))

        retention_on_specific_days = feature.RetentionRateOnSpecificDays['retention_on_specific_days']
        if len(retention_on_specific_days) > 0:
            retention_on_days_df   = pd.DataFrame(retention_on_specific_days)  # 'day' column is fine as-is
            plot_bar_chart(
                data_frame    = retention_on_days_df,
                x_column      = 'day',
                y_column      = 'retention_rate',
                title         = 'Retention on Specific Days (After registration)',
                x_label       = 'day',
                y_label       = 'Retention',
                color_palette = 'Set3',
                file_path     = os.path.join(location, f'{featureName}_retention_on_specific_days'))

        retention_in_specific_intervals = feature.RetentionRateInSpecificIntervals['retention_in_specific_interval']
        if len(retention_in_specific_intervals) > 0:
            retention_intervals_df = pd.DataFrame(retention_in_specific_intervals)
            plot_bar_chart(
                data_frame    = retention_intervals_df,
                x_column      = 'interval',
                y_column      = 'retention_rate',
                title         = 'Retention Rate in Specific Intervals',
                x_label       = 'Interval',
                y_label       = 'Retention',
                color_palette = 'Purples_d',
                file_path     = os.path.join(location, f'{featureName}_retention_in_specific_intervals'))

        # if len(feature.DropOffPoints) > 0:
        #     drop_off_points_df     = pd.DataFrame(feature.DropOffPoints)
        #     plot_bar_chart(
        #         data_frame    = drop_off_points_df,
        #         x_column      = 'event_name',
        #         y_column      = 'dropoff_rate',
        #         title         = 'Drop-Off Points by Event',
        #         x_label       = 'Events',
        #         y_label       = 'Drop-Off Rate',
        #         color_palette = 'Purples_d',
        #         file_path     = os.path.join(location, f'{feature}_retention_in_specific_intervals'))
        
        if feature.Feature == 'medication' and medication_management_metrics:
            medication_data = medication_management_metrics[0]
            if medication_data:
                medication_labels = ['Taken', 'Not Taken', 'Not Specified']
                medication_values = [
                    medication_data['medication_taken_count'],
                    medication_data['medication_missed_count'],
                    medication_data['medication_not_answered_count']
                ]

                medication_df = pd.DataFrame({
                    'Status': medication_labels,
                    'Count': medication_values
                })

                plot_pie_chart(
                    data_frame=medication_df,
                    label_column='Status',
                    value_column='Count',
                    title='Medication Management',
                    file_path=os.path.join(location, f'{featureName}_medication_management')
                )

    except Exception as e:
        print(f"Error generating feature engagement images: {e}")
        return False

    return True

###############################################################################
