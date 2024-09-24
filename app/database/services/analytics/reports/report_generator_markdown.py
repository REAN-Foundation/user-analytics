
import os
from typing import List

import pandas as pd

from app.database.services.analytics.common import get_analytics_template_path
from app.database.services.analytics.reports.feature_generator_markdown import generate_all_feature_engagement_markdown, generate_engagement_metrics_table_content
from app.database.services.analytics.reports.report_utilities import add_table_to_markdown, reindex_dataframe_to_all_missing_dates
from app.domain_types.schemas.analytics import (
    EngagementMetrics
)

###############################################################################

async def generate_report_markdown(
        markdown_file_path: str,
        metrics: EngagementMetrics) -> bool:

    # Generate the report
    template_path_ = get_analytics_template_path()
    template_path = os.path.join(template_path_, "analytics-report-template.md")
    template_str = ""
    with open(template_path, "r") as file:
        template_str = file.read()

    # Replace the placeholders in the template
    # template_str = template_str.replace("{{report_title}}", metrics.title)

    image_width = 1300

    report_details_table_str = generate_report_details_table(metrics)
    template_str = template_str.replace("{{report_details_table}}", report_details_table_str)

    basic_statistics_overview_table_str = generate_basic_statistics_overview_table(metrics)
    template_str = template_str.replace("{{basic_statistics_overview_table}}", basic_statistics_overview_table_str)

    registration_history_chart_str = f"""<img src="./registration_history.png" width="{image_width}">"""
    template_str = template_str.replace("{{registration_history_chart}}", registration_history_chart_str)

    deregistration_history_chart_str = f"""<img src="./deregistration_history.png" width="{image_width}">"""
    template_str = template_str.replace("{{deregistration_history_chart}}", deregistration_history_chart_str)
    
    registration_deregistration_table_str = generate_registration_deregistration_table(metrics)
    template_str = template_str.replace("{{registration_deregistration_table}}", registration_deregistration_table_str)

    age_distribution_chart_str = f"""<img src="./age_distribution.png" width="{image_width}">"""
    template_str = template_str.replace("{{age_distribution_chart}}", age_distribution_chart_str)

    age_distribution_table_str = generate_age_distribution_table(metrics)
    template_str = template_str.replace("{{age_distribution_table}}", age_distribution_table_str)

    gender_distribution_chart_str = f"""<img src="./patient_gender_groups.png" width="{image_width}">"""
    template_str = template_str.replace("{{gender_distribution_chart}}", gender_distribution_chart_str)

    gender_distribution_table_str = generate_gender_distribution_table(metrics)
    template_str = template_str.replace("{{gender_distribution_table}}", gender_distribution_table_str)
    
    ethnicity_distribution_chart_str = f"""<img src="./patient_ethnicity_groups.png" width="{image_width}">"""
    template_str = template_str.replace("{{ethnicity_distribution_chart}}", ethnicity_distribution_chart_str)

    ethnicity_distribution_table_str = generate_ethnicity_distribution_table(metrics)
    template_str = template_str.replace("{{ethnicity_distribution_table}}", ethnicity_distribution_table_str)

    race_distribution_chart_str = f"""<img src="./patient_race_groups.png" width="{image_width}">"""
    template_str = template_str.replace("{{race_distribution_chart}}", race_distribution_chart_str)

    race_distribution_table_str = generate_race_distribution_table(metrics)
    template_str = template_str.replace("{{race_distribution_table}}", race_distribution_table_str)

    health_system_distribution_chart_str = f"""<img src="./health_system_distribution.png" width="{image_width}">"""
    template_str = template_str.replace("{{health_system_distribution_chart}}", health_system_distribution_chart_str)

    health_system_distribution_table_str = generate_health_system_distribution_table(metrics)
    template_str = template_str.replace("{{health_system_distribution_table}}", health_system_distribution_table_str)

    hospital_distribution_chart_str = f"""<img src="./hospital_distribution.png" width="{image_width}">"""
    template_str = template_str.replace("{{hospital_affiliation_distribution_chart}}", hospital_distribution_chart_str)

    hospital_distribution_table_str = generate_hospital_affiliation_distribution_table(metrics)
    template_str = template_str.replace("{{hospital_affiliation_distribution_table}}", hospital_distribution_table_str)

    caregiver_or_stroke_survivor_distribution_chart_str = f"""<img src="./survivor_caregiver_distribution.png" width="{image_width}">"""
    template_str = template_str.replace("{{caregiver_or_stroke_survivor_distribution_chart}}", caregiver_or_stroke_survivor_distribution_chart_str)

    caregiver_or_stroke_survivor_distribution_table_str = generate_caregiver_or_stroke_survivor_distribution_table(metrics)
    template_str = template_str.replace("{{caregiver_or_stroke_survivor_distribution_table}}", caregiver_or_stroke_survivor_distribution_table_str)
    
    daily_active_users_chart_str = f"""<img src="./daily_active_users.png" width="{image_width}">"""
    template_str = template_str.replace("{{daily_active_users_chart}}", daily_active_users_chart_str)

    daily_active_users_table_str = generate_daily_active_users_table(metrics)
    template_str = template_str.replace("{{daily_active_users_table}}", daily_active_users_table_str)

    weekly_active_users_chart_str = f"""<img src="./weekly_active_users.png" width="{image_width}">"""
    template_str = template_str.replace("{{weekly_active_users_chart}}", weekly_active_users_chart_str)

    weekly_active_users_table_str = generate_weekly_active_users_table(metrics)
    template_str = template_str.replace("{{weekly_active_users_table}}", weekly_active_users_table_str)

    monthly_active_users_chart_str = f"""<img src="./monthly_active_users.png" width="{image_width}">"""
    template_str = template_str.replace("{{monthly_active_users_chart}}", monthly_active_users_chart_str)

    monthly_active_users_table_str = generate_monthly_active_users_table(metrics)
    template_str = template_str.replace("{{monthly_active_users_table}}", monthly_active_users_table_str)

    retention_rate_on_days_chart_str = f"""<img src="./retention_on_specific_days.png" width="{image_width}">"""
    template_str = template_str.replace("{{retention_rate_On_specific_days_chart}}", retention_rate_on_days_chart_str)

    retention_rate_on_days_table_str = generate_retention_rate_on_days_table(metrics)
    template_str = template_str.replace("{{retention_rate_On_specific_days_table}}", retention_rate_on_days_table_str)

    retention_rate_on_interval_chart_str = f"""<img src="./retention_in_specific_intervals.png" width="{image_width}">"""
    template_str = template_str.replace("{{retention_rate_in_specific_intervals_chart}}", retention_rate_on_interval_chart_str)

    retention_rate_on_interval_table_str = generate_retention_rate_on_interval_table(metrics)
    template_str = template_str.replace("{{retention_rate_in_specific_intervals_table}}", retention_rate_on_interval_table_str)

    login_frequency_chart_str = f"""<img src="./login_frequency.png" width="{image_width}">"""
    template_str = template_str.replace("{{login_frequency_monthly_chart}}", login_frequency_chart_str)

    login_frequency_table_str = generate_login_frequency_table(metrics)
    template_str = template_str.replace("{{login_frequency_monthly_table}}", login_frequency_table_str)

    most_commonly_visited_features_table_str = genrate_most_Commonly_Visited_Features(metrics)
    template_str = template_str.replace("{{most_commonly_used_features_table}}", most_commonly_visited_features_table_str)
    
    feature_engagement_table_content_str = generate_engagement_metrics_table_content(metrics)
    template_str = template_str.replace("{{feature_engagement_table_content}}", feature_engagement_table_content_str)
    
    all_features_engagement_str = generate_all_feature_engagement_markdown(metrics.FeatureMetrics)
    template_str = template_str.replace("{{all_features_data}}", all_features_engagement_str)

    # Save the report
    with open(markdown_file_path, "w") as file:
        file.write(template_str)

    return True

###############################################################################

def generate_report_details_table(metrics: EngagementMetrics) -> str:

    tenant_code = metrics.TenantId if metrics.TenantId is not None else "Unspecified"
    tenant_name = metrics.TenantName if metrics.TenantName is not None else "Unspecified"
    start_date = metrics.StartDate.strftime('%Y-%m-%d') if metrics.StartDate is not None else "Unspecified"
    end_date = metrics.EndDate.strftime('%Y-%m-%d') if metrics.EndDate is not None else "Unspecified"
    report_details_table =  f"""
| Filter       | Value                     | Description                                  |
|--------------|---------------------------|----------------------------------------------|
| Tenant Code  | {tenant_code} | Unique identifier for the tenant.            |
| Tenant Name  | {tenant_name} | Name of the tenant/organization              |
| Start Date   | {start_date} | Start date of the analysis period.           |
| End Date     | {end_date} | End date of the analysis period.             |
"""

    return report_details_table

def generate_basic_statistics_overview_table(metrics: EngagementMetrics) -> str:
    
    metrics = metrics.BasicStatistics
    total_users = metrics.TotalUsers if metrics.TotalUsers is not None else "Unspecified"
    total_patients = metrics.TotalPatients if metrics.TotalPatients is not None else "Unspecified"
    total_active_patients = metrics.TotalActivePatients if metrics.TotalActivePatients is not None else "Unspecified"
    
    basic_statistics_table = f"""
| Name                  | Values | Description                                  |
|-----------------------|--------|----------------------------------------------|
| Total Users           | {total_users} | Overall count of users associated with the tenant. |
| Total Patients        | {total_patients} | Total number of patients registered within the system. |
| Total Active Patients | {total_active_patients} | Total number of active (Not-deleted) patients.|
"""
    
    return basic_statistics_table

def generate_registration_deregistration_table(metrics: EngagementMetrics) -> str:
    patient_registration_history_df = pd.DataFrame(metrics.BasicStatistics.PatientRegistrationHistory)
    patient_deregistration_history_df = pd.DataFrame(metrics.BasicStatistics.PatientDeregistrationHistory)
    
    patient_registration_history_df = reindex_dataframe_to_all_missing_dates(
            data_frame=patient_registration_history_df,
            date_col='month',
            fill_col='user_count',
        )
    patient_deregistration_history_df = reindex_dataframe_to_all_missing_dates(
            data_frame=patient_deregistration_history_df,
            date_col='month',
            fill_col='user_count',
        )

    df_combined = pd.merge(
        patient_registration_history_df[['month', 'user_count']].rename(columns={'user_count': 'registration_count'}),
        patient_deregistration_history_df[['month', 'user_count']].rename(columns={'user_count': 'deregistration_count'}),
        on='month',
        how='outer'
    ).fillna(0)
    
    registration_deregistration_table = add_table_to_markdown(
        data_frame = df_combined,
        rename_columns = {'month': 'Month', 'registration_count': 'Registration Count', 'deregistration_count': 'Deregistration Count'}
    )
    
    return registration_deregistration_table   

def generate_age_distribution_table(metrics: EngagementMetrics) -> str:
    age_distribution_df = pd.DataFrame(metrics.BasicStatistics.PatientDemographics.AgeGroups)
    age_distribution_table = add_table_to_markdown(
        data_frame = age_distribution_df, 
        rename_columns = {'age_group': 'Age Group', 'count': 'Count'}
    )
    return age_distribution_table          
   
def generate_gender_distribution_table(metrics: EngagementMetrics) -> str:
    gender_distribution_df = pd.DataFrame(metrics.BasicStatistics.PatientDemographics.GenderGroups)
    gender_distribution_table = add_table_to_markdown(
        data_frame = gender_distribution_df,
        rename_columns = {'gender': 'Gender', 'count': 'Count'}
    )
    return gender_distribution_table   

def generate_ethnicity_distribution_table(metrics: EngagementMetrics) -> str:
    ethnicity_distribution_df = pd.DataFrame(metrics.BasicStatistics.PatientDemographics.EthnicityGroups)
    ethnicity_distribution_df['ethnicity'] = ethnicity_distribution_df['ethnicity'].replace('', 'Unspecified').fillna('Unspecified')
    
    ethnicity_distribution_table = add_table_to_markdown(
        data_frame = ethnicity_distribution_df,
        rename_columns = {'ethnicity': 'Ethnicity', 'count': 'Count'}
    )
    return ethnicity_distribution_table   

def generate_race_distribution_table(metrics: EngagementMetrics) -> str:
    race_distribution_df = pd.DataFrame(metrics.BasicStatistics.PatientDemographics.RaceGroups)
    race_distribution_df['race'] = race_distribution_df['race'].replace('', 'Unspecified').fillna('Unspecified')
    
    race_distribution_table = add_table_to_markdown(
        data_frame = race_distribution_df,
        rename_columns = {'race': 'Race', 'count': 'Count'}
    )
    return race_distribution_table  
 
def generate_health_system_distribution_table(metrics: EngagementMetrics) -> str:
    health_system_distribution_df = pd.DataFrame(metrics.BasicStatistics.PatientDemographics.HealthSystemDistribution)
    health_system_distribution_table = add_table_to_markdown(
        data_frame = health_system_distribution_df,
        rename_columns = {'health_system': 'Health System', 'count': 'Count'}
    )
    return health_system_distribution_table 

def generate_hospital_affiliation_distribution_table(metrics: EngagementMetrics) -> str:
    hospital_affiliation_distribution_df = pd.DataFrame(metrics.BasicStatistics.PatientDemographics.HospitalDistribution)
    hospital_affiliation_distribution_table = add_table_to_markdown(
        data_frame = hospital_affiliation_distribution_df,
        rename_columns = {'hospital': 'Hospital', 'count': 'Count'}
    )
    return hospital_affiliation_distribution_table 
    
def generate_caregiver_or_stroke_survivor_distribution_table(metrics: EngagementMetrics) -> str:
    caregiver_or_stroke_survivor_distribution_df = pd.DataFrame(metrics.BasicStatistics.PatientDemographics.SurvivorOrCareGiverDistribution)
    caregiver_or_stroke_survivor_distribution_table = add_table_to_markdown(
        data_frame = caregiver_or_stroke_survivor_distribution_df,
        rename_columns = {'caregiver_status': 'Caregiver Status', 'count': 'Count'}
    )
    return caregiver_or_stroke_survivor_distribution_table 

def generate_daily_active_users_table(metrics :EngagementMetrics)-> str:
    daily_active_users_df = pd.DataFrame(metrics.GenericMetrics.DailyActiveUsers)
    daily_active_users_df_= reindex_dataframe_to_all_missing_dates(
        data_frame = daily_active_users_df, 
        date_col = 'activity_date',
        fill_col = 'daily_active_users',
        frequency = 'daily'
    )
    daily_active_users_table = add_table_to_markdown(
        data_frame = daily_active_users_df_,
        rename_columns = {'activity_date':'Activity Date','daily_active_users':'Daily Active Users'}
    )
    return daily_active_users_table

def generate_weekly_active_users_table(metrics :EngagementMetrics)-> str:
    weekly_active_users_df = pd.DataFrame(metrics.GenericMetrics.WeeklyActiveUsers)
    weekly_active_users_df_= reindex_dataframe_to_all_missing_dates(
        weekly_active_users_df,
        start_date_col = 'week_start_date',
        end_date_col = 'week_end_date',
        fill_col = 'weekly_active_users',
        frequency = 'weekly'
    )
    weekly_active_users_table=add_table_to_markdown(
        data_frame = weekly_active_users_df_,
        rename_columns = {'week_start_date':'Week Start Date','week_end_date':'Week End Date','weekly_active_users':'Weekly Active Users'}
    )
    return weekly_active_users_table

def generate_monthly_active_users_table(metrics :EngagementMetrics)-> str:
    monthly_active_users_df = pd.DataFrame(metrics.GenericMetrics.MonthlyActiveUsers)
    monthly_active_users_df = reindex_dataframe_to_all_missing_dates(
        data_frame = monthly_active_users_df, 
        date_col = 'activity_month',
        fill_col = 'monthly_active_users',
    )
    monthly_active_users_table = add_table_to_markdown(
        data_frame = monthly_active_users_df,
        rename_columns = {'activity_month':'activity_month','monthly_active_users':'Monthly Active Users'}
    )
    return monthly_active_users_table

def generate_retention_rate_on_days_table(metrics :EngagementMetrics)-> str:
    retention_rate_on_days_df = pd.DataFrame(metrics.GenericMetrics.RetentionRateOnSpecificDays['retention_on_specific_days'])
    retention_rate_on_days_table = add_table_to_markdown(
        data_frame = retention_rate_on_days_df,
        rename_columns = {'day':'Day','returning_users':'Returning Users','retention_rate':'Retention Rate'}
    )
    return retention_rate_on_days_table

def generate_retention_rate_on_interval_table(metrics :EngagementMetrics)-> str:
    retention_rate_on_interval_df = pd.DataFrame(metrics.GenericMetrics.RetentionRateInSpecificIntervals['retention_in_specific_interval'])
    retention_rate_on_interval_table = add_table_to_markdown(
        data_frame = retention_rate_on_interval_df,
        rename_columns = {'interval':'Interval','returning_users':'Returning Users','retention_rate':'Retention Rate'}
    )
    return retention_rate_on_interval_table

def generate_login_frequency_table(metrics :EngagementMetrics)-> str:
    login_frequency_df = pd.DataFrame(metrics.GenericMetrics.LoginFrequency)
    login_frequency_table = add_table_to_markdown(
        data_frame = login_frequency_df,
        rename_columns = {'month':'Month','login_count':'Login Count'}
    )
    return login_frequency_table

def genrate_most_Commonly_Visited_Features(metrics : EngagementMetrics)-> str:
    most_commonly_visited_features_df = pd.DataFrame(metrics.GenericMetrics.MostCommonlyVisitedFeatures)
    most_commonly_visited_features_table = add_table_to_markdown(
        data_frame = most_commonly_visited_features_df,
        rename_columns = {'month':'Month','feature':'Feature','feature_usage_count':'Feature Usage Count'}
    )
    return most_commonly_visited_features_table


