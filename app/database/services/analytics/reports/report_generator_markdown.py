import os
from typing import List

import pandas as pd
from app.database.services.analytics.common import get_report_folder_path
from app.database.services.analytics.reports.report_generator_excel import read_json_file
from app.database.services.analytics.reports.report_utilities import reindex_dataframe_to_all_dates
from app.domain_types.schemas.analytics import (
    BasicAnalyticsStatistics,
    EngagementMetrics,
    FeatureEngagementMetrics,
    GenericEngagementMetrics
)

async def generate_report_markdown() -> str:
    analysis_code = '4'
    reports_path = get_report_folder_path()
    report_folder_path = os.path.join(reports_path, f"user_engagement_report_{analysis_code}")
    report_file_path = os.path.join(report_folder_path, f"user_engagement_report_{analysis_code}.md")
    
    if not os.path.exists(report_folder_path):
        os.makedirs(report_folder_path, exist_ok=True)

    basic_analysis_data_path = 'test_data/basic_statistic.json'
    basic_analysis_data = read_json_file(basic_analysis_data_path)
    metrics = BasicAnalyticsStatistics(**basic_analysis_data)
    
    # Constraints Table
    constraints_df = pd.DataFrame({
        'Filter': ['Tenant Code', 'Tenant Name', 'Start Date', 'End Date'],
        'Value': ['unspecified', 'American Heart Association', '2023-01-01', '2023-01-31'],
        'Description': ['Unique identifier for the tenant.', 'Name of the tenant/organization', 'Start date of the analysis period.', 'End date of the analysis period.']
    })
    constraints_md = constraints_df.to_markdown(index=False)
    
    # Basic Overview Table
    basic_overview_df = pd.DataFrame({
        'Property': [
            'Tenant ID',
            'Tenant Name',
            'Start Date',
            'End Date',
            'Total Users',
            'Total Patients',
            'Total Active Patients'
        ],
        'Value': [
            metrics.TenantId,
            metrics.TenantName,
            metrics.StartDate.strftime('%Y-%m-%d'),
            metrics.EndDate.strftime('%Y-%m-%d'),
            metrics.TotalUsers,
            metrics.TotalPatients,
            metrics.TotalActivePatients
        ]
    })
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
    
    basic_statistics_table = basic_overview_df.to_markdown(index=False)
    registration_history_table = dataframe_to_markdown(registration_history_df_filled, ['month', 'user_count'])
    deregistration_history_table = dataframe_to_markdown(deregistration_history_df_filled, ['month', 'user_count'])

    # Format the markdown content
    # markdown_content = md_template.format(
    #     basic_statistics_table=basic_statistics_table,
    #     registration_history_table=registration_history_table,
    #     deregistration_history_table=deregistration_history_table
    # )

    # Using a template string
    md_template = f"""# User Analytics Report

## Table of Contents

- [User Analytics Report](#user-analytics-report)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Basic Statistics](#basic-statistics)
    - [Overview](#overview)
    - [Demographics](#demographics)
  - [Generic Engagement Metrics](#generic-engagement-metrics)
    - [Daily, Weekly, and Monthly Active Users](#daily-weekly-and-monthly-active-users)
    - [Retention Rates on specific days](#retention-rates-on-specific-days)
    - [Retention Rates during specific intervals](#retention-rates-during-specific-intervals)
    - [Login Frequency](#login-frequency)
    - [Average Session Duration](#average-session-duration)
    - [Most Commonly Visited Screens](#most-commonly-visited-screens)
    - [Most Commonly Used Features](#most-commonly-used-features)
  - [Feature Engagement Metrics](#feature-engagement-metrics)
    - [Feature Engagement Metrics Definitions](#feature-engagement-metrics-definitions)
      - [Feature Access Frequency](#feature-access-frequency)
      - [Average Usage Duration](#average-usage-duration)
      - [Feature Engagement Rate](#feature-engagement-rate)
      - [Feature Retention Rate on specific days](#feature-retention-rate-on-specific-days)
      - [Feature Retention during specific intervals](#feature-retention-during-specific-intervals)
      - [Feature Drop-Off Points](#feature-drop-off-points)
    - [Medication Engagement Metrics](#medication-engagement-metrics)
      - [Monthly Medication Access Frequency](#monthly-medication-access-frequency)
      - [Monthly Average Medication Usage Duration](#monthly-average-medication-usage-duration)
      - [Medication Feature Engagement Rate](#medication-feature-engagement-rate)
      - [Medication Feature Retention Rate on specific days](#medication-feature-retention-rate-on-specific-days)
      - [Medication Feature Retention during specific intervals](#medication-feature-retention-during-specific-intervals)
      - [Medication Feature Drop-Off Points](#medication-feature-drop-off-points)
    - [Appendix A:](#appendix-a-)
        - [Daily Registration and Deregistration History Table](#daily-registration-and-deregistration-history-table)
        - [Weekly Registration and Deregistration History Table](#weekly-registration-and-deregistration-history-table)
        - [Monthly Registration and Deregistration History Table](#monthly-registration-and-deregistration-history-table)
        - [Daily Active Users Table](#daily-active-users-table)
        - [Weekly Active Users Table](#weekly-active-users-table)
        - [Monthly Active Users Table](#monthly-active-users-table)

---

## Introduction

This report provides an analysis of general usage statistics, system-wide and feature-wise user engagement metrics.

The analysis is performed considering the following constraints.

{constraints_md}

## Basic Statistics

This section provides an overview of the basic analytics related to the tenant, including the total number of users, patient statistics, and registration/deregistration history.

### Overview

{basic_statistics_table}

### Patient Registration History

{registration_history_table}

![Patient Registration History]({os.path.join('patient_registration_history.png')})

### Patient Deregistration History

{deregistration_history_table}

![Patient Deregistration History]({os.path.join('patient_deregistration_history.png')})

"""

    with open(report_file_path, 'w') as file:
        file.write(md_template)

    return report_file_path

###############################################################################


def dataframe_to_markdown(data_frame: pd.DataFrame, columns: List[str]) -> str:
    return data_frame[columns].to_markdown(index=False)


############################################################################