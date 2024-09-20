import io
import os
import pandas as pd
from app.common.utils import print_exception
from app.database.services.analytics.common import get_report_folder_temp_path
from app.database.services.analytics.reports.feature_generator_excel import feature_engagement
from app.database.services.analytics.reports.report_utilities import(
    create_chart,
    reindex_dataframe_to_all_missing_dates,
    write_data_to_excel,
    write_grouped_data_to_excel
)
from app.domain_types.schemas.analytics import (
    BasicAnalyticsStatistics,
    EngagementMetrics,
    FeatureEngagementMetrics,
    GenericEngagementMetrics
)
from datetime import datetime
from app.modules.storage.provider.awa_s3_storage_service import AwsS3StorageService

#########################################################################################

async def generate_report_excel(
        analysis_code: str,
        metrics: EngagementMetrics) -> str | None:
    try:
        reports_path = get_report_folder_temp_path()
        excel_file_path = os.path.join(reports_path, f"report_{analysis_code}.xlsx")

        with io.BytesIO() as excel_buffer:
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                await add_basic_analytics_statistics(metrics.BasicStatistics, writer)
                await add_patient_demographics_data(metrics.BasicStatistics, writer)
                await add_active_users_data(metrics.GenericMetrics, writer)
                await add_generic_engagement_data(metrics.GenericMetrics, writer)
                await add_most_visited_feature(metrics.GenericMetrics, writer)
                await add_most_visited_screens(metrics.GenericMetrics, writer)
                await add_feature_engagement_data(metrics.FeatureMetrics, writer)

            excel_buffer.seek(0)
            storage = AwsS3StorageService()
            file_name = f"analytics_report_{analysis_code}.xlsx"
            await storage.upload_excel_or_pdf(excel_buffer, file_name)

    except Exception as e:
        print_exception(e)
        return excel_file_path

###################################################################################

async def add_basic_analytics_statistics(basic_analytics: BasicAnalyticsStatistics, writer) -> bool:
    try:
        df_stats = pd.DataFrame({
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
                basic_analytics.TenantId,
                basic_analytics.TenantName,
                basic_analytics.StartDate.strftime('%Y-%m-%d'),
                basic_analytics.EndDate.strftime('%Y-%m-%d'),
                basic_analytics.TotalUsers,
                basic_analytics.TotalPatients,
                basic_analytics.TotalActivePatients
            ]
        })

        df_stats['Value'] = df_stats['Value'].fillna("Unspecified")
        sheet_name = 'Basic Analytics Statistics'
        df_stats.to_excel(writer, sheet_name=sheet_name, index=False, header=False, startrow=2, startcol=1)
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]

        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'align': 'left',
            'valign': 'vcenter'
        })

        field_bold_format = workbook.add_format({
            'bold': True,
            'align': 'left',
        })

        value_format = workbook.add_format({
            'align': 'left',
        })

        worksheet.merge_range('B1:C1', 'Basic Analytics Statistics', title_format)

        for row_num in range(len(df_stats)):
            worksheet.write(row_num + 2, 1, df_stats.at[row_num, 'Property'], field_bold_format)
            worksheet.write(row_num + 2, 2, df_stats.at[row_num, 'Value'], value_format)

        if basic_analytics.PatientRegistrationHistory and basic_analytics.PatientDeregistrationHistory:
            patient_registration_history_df = pd.DataFrame(basic_analytics.PatientRegistrationHistory)
            paitent_deregistration_history_df = pd.DataFrame(basic_analytics.PatientDeregistrationHistory)

            patient_registration_history_df = reindex_dataframe_to_all_missing_dates(
                data_frame = patient_registration_history_df,
                date_col = 'month',
                fill_col = 'user_count',
            )
            paitent_deregistration_history_df = reindex_dataframe_to_all_missing_dates(
                data_frame = paitent_deregistration_history_df,
                date_col = 'month',
                fill_col = 'user_count',
            )

            df_combined = pd.merge(
                patient_registration_history_df[['month', 'user_count']].rename(columns={'user_count': 'registration_count'}),
                paitent_deregistration_history_df[['month', 'user_count']].rename(columns={'user_count': 'deregistration_count'}),
                on='month',
                how='outer'
            ).fillna(0)

            startrow_combined_data = 13
            df_combined = write_data_to_excel(
                data_frame = df_combined,
                sheet_name = sheet_name,
                start_row = startrow_combined_data,
                start_col = 1,
                writer = writer,
                title = 'Patient Registration & Deregistration History',
                rename_columns = {'month': 'Month', 'registration_count': 'Registration Count', 'deregistration_count': 'Deregistration Count'}
            )
            patient_registration_chart = create_chart(
                workbook = workbook,
                chart_type = 'column',
                series_name = 'Patient Registration Count',
                sheet_name = sheet_name,
                start_row = 13,
                start_col = 1,
                df_len = len(df_combined),
                value_col = 2,
            )
            worksheet.insert_chart('G3', patient_registration_chart)

            patient_deregistration_chart = create_chart(
                workbook = workbook,
                chart_type = 'column',
                series_name = 'Patient Deregistration Count',
                sheet_name = sheet_name,
                start_row = 13,
                start_col = 1,
                df_len = len(df_combined),
                value_col = 3,
            )

            worksheet.insert_chart('G20', patient_deregistration_chart)
            worksheet.set_column('D:D', 20,value_format)
            worksheet.set_column('B:B', 20, value_format)
            worksheet.set_column('C:C', 20, value_format)

    except Exception as e:
        print_exception(e)
        return False

    return True

async def add_patient_demographics_data(basic_analytics: BasicAnalyticsStatistics, writer) -> bool:
    try:
        sheet_name = 'Patient Demographics'
        if sheet_name not in writer.sheets:
            worksheet = writer.book.add_worksheet(sheet_name)
        else:
            worksheet = writer.sheets[sheet_name]

        title = "Patient Demographic Report"
        worksheet.merge_range('A1:Z1', title, writer.book.add_format({'bold': True, 'font_size': 16, 'align': 'center'}))

        patient_demographics = basic_analytics.PatientDemographics

        start_row = 3
        start_col = 1
        if patient_demographics.AgeGroups:
            df_age = pd.DataFrame(patient_demographics.AgeGroups)
            df_age = write_data_to_excel(
                data_frame = df_age,
                sheet_name = sheet_name,
                start_row = start_row,
                start_col = start_col,
                writer = writer,
                title = 'Age Distribution',
                rename_columns = {'age_group': 'Age Group', 'count': 'Count'}
            )
            chart_age = create_chart(
                workbook = writer.book,
                chart_type = 'pie',
                series_name = 'Age Distribution',
                sheet_name = sheet_name,
                start_row = start_row,
                start_col = start_col,
                df_len = len(df_age),
                value_col = start_col + 1
            )
            worksheet.insert_chart(start_row, 4, chart_age)
            start_row += len(df_age) + 13

        if patient_demographics.GenderGroups:
            df_gender = pd.DataFrame(patient_demographics.GenderGroups)
            df_gender = write_data_to_excel(
                data_frame = df_gender,
                sheet_name = sheet_name,
                start_row = start_row,
                start_col = 1,
                writer = writer,
                title = 'Gender Distribution',
                rename_columns = {'gender': 'Gender', 'count': 'Count'}
            )
            chart_gender = create_chart(
                workbook = writer.book,
                chart_type = 'pie',
                series_name = 'Gender Distribution',
                sheet_name = sheet_name,
                start_row = start_row,
                start_col = start_col,
                df_len = len(df_gender),
                value_col = start_col+1
            )
            worksheet.insert_chart(start_row, 4, chart_gender)
            start_row += len(df_gender) + 13

        if patient_demographics.EthnicityGroups:
            df_ethnicity = pd.DataFrame(patient_demographics.EthnicityGroups)
            df_ethnicity['ethnicity'] = df_ethnicity['ethnicity'].replace('', 'Unspecified').fillna('Unspecified')
            df_ethnicity = write_data_to_excel(
                data_frame = df_ethnicity,
                sheet_name = sheet_name,
                start_row = start_row,
                start_col = start_col,
                writer = writer,
                title = 'Ethnicity Distribution',
                rename_columns = {'ethnicity': 'Ethnicity', 'count': 'Count'}
            )
            chart_ethnicity = create_chart(
                workbook = writer.book,
                chart_type = 'pie',
                series_name = 'Ethnicity Distribution',
                sheet_name = sheet_name,
                start_row = start_row,
                start_col = 1,
                df_len = len(df_ethnicity),
                value_col = start_col + 1
            )
            worksheet.insert_chart(start_row, 4, chart_ethnicity)
            start_row += len(df_ethnicity) + 13

        if patient_demographics.SurvivorOrCareGiverDistribution:
            df_survivor = pd.DataFrame(patient_demographics.SurvivorOrCareGiverDistribution)
            df_survivor = write_data_to_excel(
                data_frame = df_survivor,
                sheet_name = sheet_name,
                start_row = start_row,
                start_col = start_col,
                writer = writer,
                title = 'Survivor/Caregiver Distribution',
                rename_columns = {'caregiver_status': 'Caregiver Status', 'count': 'Count'}
            )
            chart_survivor = create_chart(
                workbook = writer.book,
                chart_type = 'pie',
                series_name = 'Survivor/Caregiver Distribution',
                sheet_name = sheet_name,
                start_row = start_row,
                start_col = start_col,
                df_len = len(df_survivor),
                value_col = start_col + 1
            )
            worksheet.insert_chart(start_row, 4, chart_survivor)

        start_row = 3
        start_col = 13
        if patient_demographics.RaceGroups:
            df_race = pd.DataFrame(patient_demographics.RaceGroups)
            df_race['race'] = df_race['race'].replace('', 'Unspecified').fillna('Unspecified')
            df_race = write_data_to_excel(
                df_race,
                sheet_name,
                start_row,
                start_col,
                writer,
                'Race Distribution',
                {'race': 'Race', 'count': 'Count'}
            )
            chart_race = create_chart(
                workbook = writer.book,
                chart_type = 'pie',
                series_name = 'Race Distribution',
                sheet_name = sheet_name,
                start_row = start_row,
                start_col = start_col,
                df_len = len(df_race),
                value_col = start_col+1
            )
            worksheet.insert_chart(start_row, start_col + 3, chart_race)
            start_row += len(df_race) + 13

        if patient_demographics.HealthSystemDistribution:
            df_health_system = pd.DataFrame(patient_demographics.HealthSystemDistribution)
            df_health_system = write_data_to_excel(
                data_frame = df_health_system,
                sheet_name = sheet_name,
                start_row = start_row,
                start_col = start_col,
                writer = writer,
                title = 'Health System Distribution',
                rename_columns = {'health_system': 'Health System', 'count': 'Count'}
            )
            chart_health_system = create_chart(
                writer.book, 'pie', 'Health System Distribution', sheet_name, start_row, start_col, len(df_health_system), value_col = start_col+1
            )
            worksheet.insert_chart(start_row, start_col + 3, chart_health_system)
            start_row += len(df_health_system) + 13

        if patient_demographics.HospitalDistribution:
            df_hospital = pd.DataFrame(patient_demographics.HospitalDistribution)
            df_hospital = write_data_to_excel(
                data_frame = df_hospital,
                sheet_name = sheet_name,
                start_row = start_row,
                start_col = start_col,
                writer = writer,
                title = 'Hospital Distribution',
                rename_columns = {'hospital': 'Hospital', 'count': 'Count'}
            )
            chart_hospital = create_chart(
                workbook = writer.book,
                chart_type ='pie',
                series_name = 'Hospital Distribution',
                sheet_name = sheet_name,
                start_row = start_row,
                start_col = start_col,
                df_len = len(df_hospital),
                value_col = start_col + 1
            )
            worksheet.insert_chart(start_row, start_col + 3, chart_hospital)
            start_row += len(df_hospital) + 13

    except Exception as e:
        print_exception(e)
        return False

    return True

#####################################################################################

async def add_active_users_data(generic_engagement_metrics: GenericEngagementMetrics, writer) -> bool:
    try:
        start_row = 3
        col_daily = 1
        col_weekly = 4
        col_monthly = 8

        sheet_name = 'Active Users'
        if sheet_name not in writer.sheets:
            worksheet = writer.book.add_worksheet(sheet_name)
        else:
            worksheet = writer.sheets[sheet_name]

        if generic_engagement_metrics.DailyActiveUsers:
            daily_active_users_df = pd.DataFrame(generic_engagement_metrics.DailyActiveUsers)
            daily_active_users_df = reindex_dataframe_to_all_missing_dates(
                data_frame = daily_active_users_df,
                date_col = 'activity_date',
                fill_col = 'daily_active_users',
                frequency = 'daily'
            )
            daily_active_users_df_ = write_data_to_excel(
                data_frame = daily_active_users_df,
                sheet_name = sheet_name,
                start_row = start_row,
                start_col = col_daily,
                writer = writer,
                title = 'Daily Active Users',
                rename_columns = {'activity_date': 'Activity Date', 'daily_active_users': 'Daily Active Users'}
            )
            daily_active_users_chart = create_chart(
                workbook = writer.book,
                chart_type = 'column',
                series_name = 'Daily Active Users',
                sheet_name = sheet_name,
                start_row = start_row,
                start_col = col_daily,
                df_len = len(daily_active_users_df_),
                value_col = col_daily + 1
            )
            worksheet.insert_chart(start_row , col_monthly + 3, daily_active_users_chart)

        if generic_engagement_metrics.WeeklyActiveUsers:
            weekly_active_users_df = pd.DataFrame(generic_engagement_metrics.WeeklyActiveUsers)
            weekly_active_users_df = reindex_dataframe_to_all_missing_dates(weekly_active_users_df, start_date_col='week_start_date', end_date_col='week_end_date', fill_col='weekly_active_users', frequency='weekly')
            weekly_active_users_df_ = write_data_to_excel(
                data_frame = weekly_active_users_df,
                sheet_name = sheet_name,
                start_row = start_row,
                start_col = col_weekly,
                writer = writer,
                title = 'Weekly Active Users',
                rename_columns = {'week_start_date': 'Week Start Date', 'week_end_date': 'Week End Date', 'weekly_active_users': 'Weekly Active Users'}
            )

            weekly_active_users_chart = create_chart(
            workbook = writer.book,
            chart_type = 'column',
            series_name = 'Weekly Active Users',
            sheet_name = sheet_name,
            start_row = start_row,
            start_col = col_weekly,
            df_len = len(weekly_active_users_df_),
            value_col = col_weekly + 2,
        )
        worksheet.insert_chart(start_row + 16, col_monthly + 3, weekly_active_users_chart)

        if generic_engagement_metrics.MonthlyActiveUsers:
            monthly_active_users_df = pd.DataFrame(generic_engagement_metrics.MonthlyActiveUsers)
            monthly_active_users_reindex = reindex_dataframe_to_all_missing_dates(
                data_frame = monthly_active_users_df,
                date_col = 'activity_month',
                fill_col = 'monthly_active_users',
            )
            monthly_active_users_df_ = write_data_to_excel(
                data_frame = monthly_active_users_reindex,
                sheet_name = sheet_name,
                start_row = start_row,
                start_col = col_monthly,
                writer = writer,
                title = 'Monthly Active Users',
                rename_columns = {'activity_month': 'Activity Month', 'monthly_active_users': 'Monthly Active Users'}
            )
            monthly_active_users_chart = create_chart(
                workbook = writer.book,
                chart_type = 'column',
                series_name = 'Monthly Active Users',
                sheet_name = sheet_name,
                start_row = start_row,
                start_col = col_monthly,
                df_len = len(monthly_active_users_df_),
                value_col = col_monthly + 1
            )
            worksheet.insert_chart(start_row + 32, col_monthly + 3, monthly_active_users_chart)

    except Exception as e:
        print_exception(e)
        return False

    return True

async def add_generic_engagement_data(generic_engagement_metrics: GenericEngagementMetrics, writer) -> bool:
    try:
        start_row = 3
        col_login_freq = 1
        col_retention_days = 14
        col_retention_intervals = 18

        sheet_name = 'Generic Engagement'
        if sheet_name not in writer.sheets:
            worksheet = writer.book.add_worksheet(sheet_name)
        else:
            worksheet = writer.sheets[sheet_name]

        if generic_engagement_metrics.LoginFrequency:
            df_login_freq = pd.DataFrame(generic_engagement_metrics.LoginFrequency)
            df_login_freq = write_data_to_excel(
                data_frame = df_login_freq,
                sheet_name = sheet_name,
                start_row = start_row,
                start_col = col_login_freq,
                writer = writer,
                title = 'Login Frequency',
                rename_columns = {'month': 'Month', 'login_count': 'Login Count'}
            )
            chart_login_freq = create_chart(
                workbook = writer.book,
                chart_type = 'column',
                series_name = 'Login Frequency',
                sheet_name = sheet_name,
                start_row = start_row,
                start_col = col_login_freq,
                df_len = len(df_login_freq),
                value_col = col_login_freq+1)
            worksheet.insert_chart(start_row , col_login_freq + 4, chart_login_freq)

        if generic_engagement_metrics.RetentionRateOnSpecificDays:
            retention_specific_days = generic_engagement_metrics.RetentionRateOnSpecificDays['retention_on_specific_days']
            retention_days_df = pd.DataFrame(retention_specific_days)
            retention_days_df_ = write_data_to_excel(
                data_frame = retention_days_df,
                sheet_name = sheet_name,
                start_row = start_row,
                start_col = col_retention_days,
                writer = writer,
                title = 'Retention Rate on Specific Days',
                rename_columns = {'day': 'Day', 'returning_users': 'Returning Users', 'retention_rate': 'Retention Rate'}
            )
            retention_rate_on_specific_days_chart = create_chart(
                workbook = writer.book,
                chart_type = 'column',
                series_name = 'Retention Rate on Specific Days',
                sheet_name = sheet_name,
                start_row = start_row,
                start_col = col_retention_days,
                df_len = len(retention_days_df_),
                value_col = col_retention_days + 2
            )
            worksheet.insert_chart(start_row, col_retention_intervals + 5, retention_rate_on_specific_days_chart)

        if generic_engagement_metrics.RetentionRateInSpecificIntervals:
            retention_intervals = generic_engagement_metrics.RetentionRateInSpecificIntervals['retention_in_specific_interval']
            retention_intervals_df = pd.DataFrame(retention_intervals)
            retention_intervals_df_ = write_data_to_excel(
                data_frame = retention_intervals_df,
                sheet_name = sheet_name,
                start_row = start_row,
                start_col = col_retention_intervals,
                writer = writer,
                title = 'Retention Rate in Specific Intervals',
                rename_columns = {'interval': 'Interval', 'returning_users': 'Returning Users', 'retention_rate': 'Retention Rate'}
            )
            retention_intervals_chart = create_chart(
                workbook=writer.book,
                chart_type = 'column',
                series_name = 'Retention Rate in Specific Intervals',
                sheet_name = sheet_name,
                start_row = start_row,
                start_col = col_retention_intervals,
                df_len = len(retention_intervals_df_),
                value_col = col_retention_intervals + 2
            )
            worksheet.insert_chart(start_row + 18, col_retention_intervals + 5, retention_intervals_chart)
    except Exception as e:
        print_exception(e)
        return False

    return True

async def add_most_visited_feature(generic_engagement_metrics: GenericEngagementMetrics, writer) -> bool:
    try:
        start_row = 3
        start_col = 1
        sheet_name = 'Most Visited Features'
        if sheet_name not in writer.sheets:
            worksheet = writer.book.add_worksheet(sheet_name)
        else:
            worksheet = writer.sheets[sheet_name]

        if generic_engagement_metrics.MostCommonlyVisitedFeatures:
            most_commonly_visited_features_df = pd.DataFrame(generic_engagement_metrics.MostCommonlyVisitedFeatures)
            write_grouped_data_to_excel(
                data_frame = most_commonly_visited_features_df,
                sheet_name = sheet_name,
                start_row = start_row,
                start_col = start_col,
                writer = writer,
                title = 'Most Visited Features',
                group_by_column = 'Month',
                feature_column = 'Feature',
                value_column = 'Usage Count',
                rename_columns = {'month': 'Month', 'feature': 'Feature', 'feature_usage_count': 'Usage Count'}
            )
    except Exception as e:
        print_exception(e)
        return False

    return True

async def add_most_visited_screens(generic_engagement_metrics: GenericEngagementMetrics, writer) -> bool:
    try:
        start_row = 3
        start_col = 1
        sheet_name = 'Most Visited Screens'

        if sheet_name not in writer.sheets:
            worksheet = writer.book.add_worksheet(sheet_name)
        else:
            worksheet = writer.sheets[sheet_name]

        if generic_engagement_metrics.MostCommonlyVisitedScreens:
            most_commonly_visited_screens_df = pd.DataFrame(generic_engagement_metrics.MostCommonlyVisitedScreens)
            write_grouped_data_to_excel(
                data_frame = most_commonly_visited_screens_df,
                sheet_name = sheet_name,
                start_row = start_row,
                start_col = start_col,
                writer = writer,
                title = 'Most Visited Screens',
                group_by_column = 'Month',
                feature_column = 'Screen',
                value_column = 'Count',
                rename_columns = {'month': 'Month', 'screen': 'Screen', 'count': 'Count'}
            )
    except Exception as e:
        print_exception(e)
        return False

    return True

################################################################################################

async def add_feature_engagement_data(feature_engagement_metrics: FeatureEngagementMetrics, writer) -> bool:
    try:
        for metrics in feature_engagement_metrics:
            sheet_name = metrics.Feature
            await feature_engagement(
                feature_feature_engagement_metrics = metrics,
                writer = writer,
                sheet_name = sheet_name
            )
    except Exception as e:
        print(f"Error generating report: {e}")
        return False
    return True

##################################################################################
