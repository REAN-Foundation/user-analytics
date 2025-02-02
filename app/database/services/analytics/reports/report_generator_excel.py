import io
import os
import pandas as pd
from app.common.utils import print_exception
from app.database.services.analytics.common import get_current_report_folder_temp_path, get_storage_key_path
from app.database.services.analytics.reports.assessment_generator_excel import assessment_engagement
from app.database.services.analytics.reports.feature_generator_excel import feature_engagement
from app.database.services.analytics.reports.report_utilities import(
    create_chart,
    add_title_and_description,
    reindex_dataframe_to_all_missing_dates,
    write_data_to_excel,
    write_grouped_data_to_excel
)
from app.domain_types.schemas.analytics import (
    AssessmentEngagementMetrics,
    BasicAnalyticsStatistics,
    EngagementMetrics,
    FeatureEngagementMetrics,
    GenericEngagementMetrics,
    HealthJourneyEngagementMetrics,
    PatientTaskEngagementMetrics
)

from app.modules.storage.storage_service import StorageService

#########################################################################################

async def generate_report_excel(
        analysis_code: str,
        metrics: EngagementMetrics) -> str | None:
    try:
        reports_path = get_current_report_folder_temp_path()
        excel_file_path = os.path.join(reports_path, f"report_{analysis_code}.xlsx")

        with io.BytesIO() as excel_buffer:
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                await add_basic_analytics_statistics(metrics.BasicStatistics, writer)
                await add_patient_demographics_data(metrics.BasicStatistics, writer)
                await add_active_users_data(metrics.GenericMetrics, writer)
                await add_generic_engagement_data(metrics.GenericMetrics, writer)
                await add_most_visited_feature(metrics.GenericMetrics, writer)
                await add_feature_engagement_data(metrics.FeatureMetrics, metrics.MedicationManagementMetrics, metrics.HealthJourneyMetrics, metrics.PatientTaskMetrics,metrics.VitalMetrics, writer)
                await add_assessments_engagement_data(metrics.AssessmentMetrics, writer)

            excel_buffer.seek(0)
            storage = StorageService()
            file_name = f"analytics_report_{analysis_code}.xlsx"
            storage_location = get_storage_key_path(analysis_code)
            await storage.upload_file_as_object(storage_location, excel_buffer, file_name)

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
                str(basic_analytics.TenantId),
                basic_analytics.TenantName,
                basic_analytics.StartDate.strftime('%Y-%m-%d'),
                basic_analytics.EndDate.strftime('%Y-%m-%d'),
                basic_analytics.TotalUsers,
                basic_analytics.TotalPatients,
                basic_analytics.TotalActivePatients
            ],
            'Description': [
                'Unique identifier for the tenant.',
                'Name of the tenant/organization.',
                'Start date of the analysis period.',
                'End date of the analysis period.',
                'Overall count of users associated with the tenant.',
                'Total number of patients registered within the system.',
                'Total number of active (Not-deleted) patients.'
            ]
        })

        start_row = 1
        start_col = 1
        graph_col=7
        title = "Basic Analytics Statistics"
        description = "This section provides an overview of the basic analytics related to the tenant, including the total number of users, patient statistics, and registration/deregistration history."

        df_stats['Value'] = df_stats['Value'].fillna("Unspecified")
        sheet_name = 'Basic Statistics'
        df_stats.to_excel(writer, sheet_name=sheet_name, index=False, header=False, startrow=5, startcol=1)
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]

        add_title_and_description(
            worksheet = worksheet,
            title = title,
            description = description,
            start_row=start_row,
            start_col = start_col,
            workbook = writer.book,
        )

        field_bold_format = workbook.add_format({
            'bold': True,
            'align': 'left',
        })

        value_format = workbook.add_format({
            'align': 'left',
        })

        for row_num in range(len(df_stats)):
            worksheet.write(row_num + 5, 1, df_stats.at[row_num, 'Property'], field_bold_format)
            worksheet.write(row_num + 5, 2, df_stats.at[row_num, 'Value'], value_format)
            worksheet.write(row_num + 5, 3, df_stats.at[row_num, 'Description'], value_format)

        start_row = len(df_stats) + 10
        if basic_analytics.PatientRegistrationHistory or basic_analytics.PatientDeregistrationHistory:
            patient_registration_history_df = pd.DataFrame(basic_analytics.PatientRegistrationHistory)
            patient_deregistration_history_df = pd.DataFrame(basic_analytics.PatientDeregistrationHistory)

            if not patient_registration_history_df.empty:
                patient_registration_history_df = reindex_dataframe_to_all_missing_dates(
                    data_frame=patient_registration_history_df,
                    date_col='month',
                    fill_col='user_count',
                )
            else:
                patient_registration_history_df = pd.DataFrame(columns=['month', 'user_count'])

            if not patient_deregistration_history_df.empty:
                patient_deregistration_history_df = reindex_dataframe_to_all_missing_dates(
                    data_frame=patient_deregistration_history_df,
                    date_col='month',
                    fill_col='user_count',
                )
            else:
                patient_deregistration_history_df = pd.DataFrame(columns=['month', 'user_count'])

            df_combined = pd.merge(
                patient_registration_history_df[['month', 'user_count']].rename(columns={'user_count': 'registration_count'}),
                patient_deregistration_history_df[['month', 'user_count']].rename(columns={'user_count': 'deregistration_count'}),
                on='month',
                how='outer'
            ).fillna(0).infer_objects(copy=False)

            df_combined = write_data_to_excel(
                data_frame=df_combined,
                sheet_name=sheet_name,
                start_row=start_row,
                start_col=start_col,
                writer=writer,
                title='Patient Registration & Deregistration History',
                rename_columns={'month': 'Month', 'registration_count': 'Registration Count', 'deregistration_count': 'Deregistration Count'},
                description='Trends of how many users registered or deregistered from the system on a given day, in a given week, or a month.'
            )

            if not df_combined.empty:
                reg_dereg_chart = workbook.add_chart({'type': 'column'})
                reg_dereg_chart.add_series({
                    'name': 'Registration',
                    'categories': [sheet_name, start_row + 3, start_col, start_row + len(df_combined), start_col],
                    'values': [sheet_name, start_row + 3, start_col + 1, start_row + len(df_combined), start_col + 1],
                })
                reg_dereg_chart.add_series({
                    'name': 'Deregistration',
                    'categories': [sheet_name, start_row + 3, start_col, start_row + len(df_combined), start_col],
                    'values': [sheet_name, start_row + 3, start_col + 2, start_row + len(df_combined), start_col + 2],
                })
                reg_dereg_chart.set_x_axis({
                    'major_gridlines': {
                        'visible': True,
                        'line': {'color': '#CCCCCC', 'dash_type': 'dot', 'transparency': 0.8}
                    }
                })
                reg_dereg_chart.set_y_axis({
                    'major_gridlines': {
                        'visible': True,
                        'line': {'color': '#CCCCCC', 'dash_type': 'dot', 'transparency': 0.8}
                    }
                })
                reg_dereg_chart.set_title({'name': 'Patient Registration & Deregistration'})
                worksheet.insert_chart('H21', reg_dereg_chart)
                worksheet.set_column('D:D', 20,value_format)
                worksheet.set_column('B:B', 20, value_format)
                worksheet.set_column('C:C', 20, value_format)
                start_row = start_row + len(patient_registration_history_df) + 10

        if len(basic_analytics.UsersDistributionByRole) > 0:
            user_distribution_by_role_df  = pd.DataFrame(basic_analytics.UsersDistributionByRole)
            user_distribution_by_role_df_ = write_data_to_excel(
                data_frame     = user_distribution_by_role_df,
                sheet_name     = sheet_name,
                start_row      = start_row,
                start_col      = start_col,
                writer         = writer,
                title          = 'Users Distribution By Role',
                rename_columns = {'registration_count': 'Registration Count', 'role_name': 'Role Name'}
            )
            user_distribution_by_role_chart = create_chart(
                workbook     = writer.book,
                chart_type   = 'pie',
                series_name  = 'Age Distribution',
                sheet_name   = sheet_name,
                start_row    = start_row,
                start_col    = start_col + 1,
                df_len       = len(user_distribution_by_role_df_),
                value_col    = start_col
            )
            worksheet.insert_chart(start_row, graph_col, user_distribution_by_role_chart)
            start_row = start_row + len(user_distribution_by_role_df_) + 12
        
        if len(basic_analytics.ActiveUsersCountAtEndOfMonth) > 0:
            
            active_users_count_at_end_of_month  = pd.DataFrame(basic_analytics.ActiveUsersCountAtEndOfMonth)
            
            active_users_count_at_end_of_month_ = write_data_to_excel(
                    data_frame     = active_users_count_at_end_of_month,
                    sheet_name     = sheet_name,
                    start_row      = start_row,
                    start_col      = start_col,
                    writer         = writer,
                    title          = 'Active Users Count At End Of Month',
                    rename_columns = {'month_end': 'Month End', 'active_user_count': 'Active User Count'}
                )

            chart = create_chart(
                workbook    = writer.book,
                chart_type  = 'area',
                series_name = 'Active Users',
                sheet_name  = sheet_name,
                start_row   = start_row,
                start_col   = start_col,
                df_len      = len(active_users_count_at_end_of_month_),
                value_col   = start_col + 1,
            )

            worksheet.insert_chart(start_row, graph_col, chart)

    except Exception as e:
        print_exception(e)
        return False

    return True

async def add_patient_demographics_data(basic_analytics: BasicAnalyticsStatistics, writer) -> bool:
    try:
        sheet_name = 'Demographics'
        if sheet_name not in writer.sheets:
            worksheet = writer.book.add_worksheet(sheet_name)
        else:
            worksheet = writer.sheets[sheet_name]

        patient_demographics = basic_analytics.PatientDemographics

        title = "Demographics"
        description = "This report provides a detailed breakdown of the demographics of patients, including age, gender, location, and other relevant metrics."

        start_row = 1
        start_col = 1

        add_title_and_description(
            worksheet = worksheet,
            title = title,
            description = description,
            start_row=start_row,
            start_col = start_col,
            workbook = writer.book,
        )

        start_row = start_row + 6
        # start_col = 1
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

        start_col = 13
        start_row = 7
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

#####################################################################################

async def add_active_users_data(generic_engagement_metrics: GenericEngagementMetrics, writer) -> bool:
    try:
        start_row = 1
        col_daily = 1
        col_weekly = 4
        col_monthly = 8

        sheet_name = 'Active Users'
        if sheet_name not in writer.sheets:
            worksheet = writer.book.add_worksheet(sheet_name)
        else:
            worksheet = writer.sheets[sheet_name]

        title = "Active users"
        description = "Total number of unique users who interact with the platform on a given duration."

        add_title_and_description(
            worksheet = worksheet,
            title = title,
            description = description,
            start_row = start_row,
            start_col = col_daily,
            workbook = writer.book,
        )

        start_row += 6
        if len(generic_engagement_metrics.DailyActiveUsers) > 0:
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

            if not daily_active_users_df.empty:
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

        if len(generic_engagement_metrics.WeeklyActiveUsers) > 0:
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

            if not weekly_active_users_df.empty:
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

        if len(generic_engagement_metrics.MonthlyActiveUsers) > 0 :
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

            if not monthly_active_users_reindex.empty:
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
        start_row = 1
        start_col = 1
        graph_pos = 7
        current_row = start_row + 6
        sheet_name = 'Generic Engagement'
        if sheet_name not in writer.sheets:
            worksheet = writer.book.add_worksheet(sheet_name)
        else:
            worksheet = writer.sheets[sheet_name]

        title = "Generic Engagement Metrics"
        description = "This section captures key metrics that provide insight into how users interact with the system, including daily activity, login frequency and retention."

        add_title_and_description(
            worksheet = worksheet,
            title = title,
            description = description,
            start_row = start_row,
            start_col = start_col,
            workbook = writer.book,
        )

        start_row = start_row + 4
        if len(generic_engagement_metrics.LoginFrequency) > 0:
            df_login_freq = pd.DataFrame(generic_engagement_metrics.LoginFrequency)
            df_login_freq = write_data_to_excel(
                data_frame = df_login_freq,
                sheet_name = sheet_name,
                start_row = current_row,
                start_col = start_col,
                writer = writer,
                title = 'Login Frequency',
                rename_columns = {'month': 'Month', 'login_count': 'Login Count'},
                description = 'Average number of times users log into the system per day, week, or month.'
            )
            if not df_login_freq.empty:
                chart_login_freq = create_chart(
                    workbook = writer.book,
                    chart_type = 'column',
                    series_name = 'Login Frequency',
                    sheet_name = sheet_name,
                    start_row = current_row + 2,
                    start_col = start_col,
                    df_len = len(df_login_freq),
                    value_col = start_col + 1)
                worksheet.insert_chart(current_row + 2, graph_pos, chart_login_freq)
            current_row = current_row + len(df_login_freq) + 6

        if len(generic_engagement_metrics.RetentionRateOnSpecificDays) > 0:
            retention_specific_days = generic_engagement_metrics.RetentionRateOnSpecificDays['retention_on_specific_days']
            retention_days_df = pd.DataFrame(retention_specific_days)
            retention_days_df_ = write_data_to_excel(
                data_frame = retention_days_df,
                sheet_name = sheet_name,
                start_row = current_row,
                start_col = start_col,
                writer = writer,
                title = 'Retention Rate on Specific Days',
                rename_columns = {'day': 'Day', 'returning_users': 'Returning Users', 'retention_rate': 'Retention Rate'},
                description = 'The percentage of users who return to the app after their first use at specific intervals (day 1, day 7, day 30). Retention rates measure user loyalty and the ability of the platform to keep users engaged over time.'
            )
            if not retention_days_df.empty:
                retention_rate_on_specific_days_chart = create_chart(
                    workbook = writer.book,
                    chart_type = 'column',
                    series_name = 'Retention Rate on Specific Days',
                    sheet_name = sheet_name,
                    start_row = current_row + 2,
                    start_col = start_col,
                    df_len = len(retention_days_df_),
                    value_col = start_col + 2
                )
            worksheet.insert_chart(current_row + 2, graph_pos, retention_rate_on_specific_days_chart)
            current_row = current_row + len(retention_days_df_) + 12

        if len(generic_engagement_metrics.RetentionRateInSpecificIntervals) > 0:
            retention_intervals = generic_engagement_metrics.RetentionRateInSpecificIntervals['retention_in_specific_interval']
            retention_intervals_df = pd.DataFrame(retention_intervals)
            retention_intervals_df_ = write_data_to_excel(
                data_frame = retention_intervals_df,
                sheet_name = sheet_name,
                start_row = current_row,
                start_col = start_col,
                writer = writer,
                title = 'Retention Rate in Specific Intervals',
                rename_columns = {'interval': 'Interval', 'returning_users': 'Returning Users', 'retention_rate': 'Retention Rate'},
                description = 'The percentage of users who return to the app after their first use at specific intervals (0-1 days, 1-3 days, 3-7 days, etc). This is just another way to look at the retention on specific days.'
            )
            if not retention_intervals_df.empty:
                retention_intervals_chart = create_chart(
                    workbook=writer.book,
                    chart_type = 'column',
                    series_name = 'Retention Rate in Specific Intervals',
                    sheet_name = sheet_name,
                    start_row = current_row + 2,
                    start_col = start_col,
                    df_len = len(retention_intervals_df_),
                    value_col = start_col + 2
                )
            worksheet.insert_chart(current_row + 2, graph_pos, retention_intervals_chart)
            current_row = current_row + len(retention_intervals_df) + 12
            
        if len(generic_engagement_metrics.MostFiredEvents) > 0:
            most_fired_events  = pd.DataFrame(generic_engagement_metrics.MostFiredEvents)
            write_data_to_excel(
                data_frame = most_fired_events,
                sheet_name = sheet_name,
                start_row = current_row,
                start_col = start_col,
                writer = writer,
                title = 'Most Fired Events',
                rename_columns = {'EventName': 'Event Name', 'event_count': 'Event Count'},
                description = 'Particular event fired for particular time'
            )
            current_row = current_row + len(most_fired_events) + 12
            
        if len(generic_engagement_metrics.MostFiredEventsByEventCategory) > 0:
            most_fired_events_by_event_category_df  = pd.DataFrame(generic_engagement_metrics.MostFiredEventsByEventCategory)
            write_data_to_excel(
                data_frame = most_fired_events_by_event_category_df,
                sheet_name = sheet_name,
                start_row = current_row,
                start_col = start_col,
                writer = writer,
                title = 'Most Fired Events By Category',
                rename_columns = {'EventCategory': 'Event Category', 'EventName': 'Event Name','event_count':'Event Count'},
                description = 'category wise event fired count'
            ) 
               
    except Exception as e:
        print_exception(e)
        return False

    return True

async def add_most_visited_feature(generic_engagement_metrics: GenericEngagementMetrics, writer) -> bool:
    try:
        start_row = 3
        start_col_visited_feature = 1
        start_col_visited_screens = 6

        sheet_name = 'Most Visited'
        if sheet_name not in writer.sheets:
            worksheet = writer.book.add_worksheet(sheet_name)
        else:
            worksheet = writer.sheets[sheet_name]

        if len(generic_engagement_metrics.MostCommonlyVisitedFeatures) > 0:
            most_commonly_visited_features_df = pd.DataFrame(generic_engagement_metrics.MostCommonlyVisitedFeatures)
            write_grouped_data_to_excel(
                data_frame = most_commonly_visited_features_df,
                sheet_name = sheet_name,
                start_row = start_row,
                start_col = start_col_visited_feature,
                writer = writer,
                title = 'Most Visited Features',
                group_by_column = 'Month',
                feature_column = 'Feature',
                value_column = 'Usage Count',
                rename_columns = {'month': 'Month', 'feature': 'Feature', 'feature_usage_count': 'Usage Count'},
                description = 'The most frequently used features within the platform, indicating user preferences and popular functionalities.'
            )
        if len(generic_engagement_metrics.MostCommonlyVisitedScreens) > 0:
            most_commonly_visited_screens_df = pd.DataFrame(generic_engagement_metrics.MostCommonlyVisitedScreens)
            write_grouped_data_to_excel(
                data_frame = most_commonly_visited_screens_df,
                sheet_name = sheet_name,
                start_row = start_row,
                start_col = start_col_visited_screens,
                writer = writer,
                title = 'Most Visited Screens',
                group_by_column = 'Month',
                feature_column = 'Screen',
                value_column = 'Count',
                rename_columns = {'month': 'Month', 'screen': 'Screen', 'count': 'Count'},
               description = 'The most frequently visited screens or features within the platform, indicating where the user spent most of their time.'
            )
    except Exception as e:
        print_exception(e)
        return False

    return True

################################################################################################

async def add_feature_engagement_data(
    feature_engagement_metrics: FeatureEngagementMetrics,
    medication_management_metrics,
    health_journey_metrics:HealthJourneyEngagementMetrics,
    patient_task_metrics:PatientTaskEngagementMetrics,
    vitals_task_metrics : list | None,
    writer) -> bool:
    try:
        for metrics in feature_engagement_metrics:
            sheet_name = metrics.Feature
            await feature_engagement(
                feature_engagement_metrics = metrics,
                writer = writer,
                sheet_name = sheet_name,
                medication_management_metrics = medication_management_metrics,
                health_journey_metrics = health_journey_metrics,
                patient_task_metrics = patient_task_metrics,
                vitals_task_metrics = vitals_task_metrics   
            )
    except Exception as e:
        print(f"Error generating feature engagement excel report: {e}")
        return False
    return True

##################################################################################

async def add_assessments_engagement_data(
    assessment_metrics: AssessmentEngagementMetrics,
    writer) -> bool:
    try:
        await assessment_engagement(
            assessment_metrics = assessment_metrics,
            writer = writer,  
        )
    except Exception as e:
        print(f"Error generating assessment engagement excel report: {e}")
        return False
    return True
