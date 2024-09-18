import os
import json
import pandas as pd
from datetime import datetime
from app.domain_types.schemas.analytics import (
    BasicAnalyticsStatistics, 
    EngagementMetrics, 
    FeatureEngagementMetrics, 
    GenericEngagementMetrics
)

############################################################################################

def get_report_folder_path() -> str:
    cwd = os.getcwd()
    today = datetime.today()
    date_timestamp = today.strftime("%Y%m%d")
    reports_path = os.path.join(cwd, 'tmp', 'analytics_reports', date_timestamp)
    os.makedirs(reports_path, exist_ok=True)
    return reports_path

def read_json_file(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def reindex_dataframe_to_all_months(df, date_col, fill_col, fill_value=0, date_format='%Y-%m'):
    df[date_col] = pd.to_datetime(df[date_col], format=date_format)
    start_date = df[date_col].min()
    end_date = df[date_col].max()
    all_dates = pd.date_range(start=start_date, end=end_date, freq='MS')
    all_dates_df = pd.DataFrame({date_col: all_dates})
    df_reindexed = pd.merge(all_dates_df, df, on=date_col, how='left').fillna({fill_col: fill_value})
    df_reindexed[date_col] = df_reindexed[date_col].dt.strftime('%Y-%m')

    return df_reindexed

def reindex_dataframe_to_all_dates(df, date_col, fill_col, fill_value=0, date_format='%Y-%m-%d'):

    df[date_col] = pd.to_datetime(df[date_col], format=date_format)
    start_date = df[date_col].min()
    end_date = df[date_col].max()
    all_dates = pd.date_range(start=start_date, end=end_date, freq='D')  # 'D' is used for daily frequency
    all_dates_df = pd.DataFrame({date_col: all_dates})
    df_reindexed = pd.merge(all_dates_df, df, on=date_col, how='left').fillna({fill_col: fill_value})
    df_reindexed[date_col] = df_reindexed[date_col].dt.strftime('%Y-%m-%d')

    return df_reindexed

def reindex_dataframe_to_all_weeks(df, start_date_col, end_date_col, fill_col, fill_value=0, date_format='%Y-%m-%d'):
    df[start_date_col] = pd.to_datetime(df[start_date_col], format=date_format)
    df[end_date_col] = pd.to_datetime(df[end_date_col], format=date_format)
    min_date = df[start_date_col].min()
    max_date = df[start_date_col].max()
    all_weeks = pd.date_range(start=min_date, end=max_date, freq='W-MON')
    
    all_weeks_df = pd.DataFrame({start_date_col: all_weeks})
    df_reindexed = pd.merge(all_weeks_df, df, on=start_date_col, how='left').fillna({fill_col: fill_value})
    df_reindexed[start_date_col] = df_reindexed[start_date_col].dt.strftime('%Y-%m-%d')
    df_reindexed[end_date_col] = df_reindexed[end_date_col].dt.strftime('%Y-%m-%d')
    
    return df_reindexed

def write_data_to_excel(df, sheet_name: str, start_row: int, start_col: int, writer, title: str, rename_columns=None):
    
    title_format = writer.book.add_format({'bold': True, 'font_size': 14, 'align': 'left'})
    data_format = writer.book.add_format({'align': 'left'})
    header_format = writer.book.add_format({'border': 0,'bold':True})
    
    worksheet = writer.sheets[sheet_name]
    worksheet.write(start_row - 2, start_col, title, title_format)
    if rename_columns:
        df.rename(columns=rename_columns, inplace=True)

    df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=start_row, startcol=start_col,)
    for i, col in enumerate(df.columns):
        worksheet.write(start_row, start_col + i, col, header_format)
        
    for i, col in enumerate(df.columns):
        max_len = max(df[col].astype(str).map(len).max(), len(col))
        worksheet.set_column(start_col + i, start_col + i, max_len, data_format)
    
    return df

def create_chart(workbook, chart_type, series_name, sheet_name, start_row, start_col, df_len, value_col, x_axis='', y_axis=''):

    chart = workbook.add_chart({'type': chart_type})
    
    chart.add_series({
        'name': series_name,
        'categories': [sheet_name, start_row + 1, start_col, start_row + df_len, start_col],
        'values': [sheet_name, start_row + 1, value_col, start_row + df_len, value_col],
    })
    
    chart.set_title({'name': f'{series_name}'})
    
    if chart_type != 'pie':
        chart.set_x_axis({
            'name': x_axis,
            'major_gridlines': {
                'visible': True,
                'line': {'color': '#CCCCCC', 'dash_type': 'dot', 'transparency': 0.8}
            }
        })
        chart.set_y_axis({
            'name': y_axis,
            'major_gridlines': {
                'visible': True,
                'line': {'color': '#CCCCCC', 'dash_type': 'dot', 'transparency': 0.8}
            }
        })
        chart.set_legend({'none': True})
    
    if chart_type == 'pie':
        chart.set_legend({
            'position': 'right',
            'font': {'bold': True, 'size': 10}
        })
    
    return chart

#####################################################################

async def generate_report_excel(
        analysis_code: str,
        metrics: EngagementMetrics) -> str | None:
    try:
        reports_path = get_report_folder_path()
        excel_file_path = os.path.join(reports_path, f"report_{analysis_code}.xlsx")
        with pd.ExcelWriter(excel_file_path, engine='xlsxwriter') as writer:
             await add_basic_analytics_statistics(metrics.BasicStatistics, writer)
             await add_patient_demographics_data(metrics.BasicStatistics, writer)
             await add_active_users_data(metrics.GenericMetrics, writer)
             await add_generic_engagement_data(metrics.GenericMetrics, writer)
             await add_feature_engagement_data(metrics.FeatureMetrics, writer)
        return excel_file_path
    except Exception as e:
        print(e)
        return ""

###################################################################################

async def add_basic_analytics_statistics(basic_analytics: BasicAnalyticsStatistics, writer) -> None:
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
    
        patient_registration_history_df = reindex_dataframe_to_all_months(
            patient_registration_history_df,
            date_col='month',
            fill_col='user_count',
        )
        paitent_deregistration_history_df = reindex_dataframe_to_all_months(
            paitent_deregistration_history_df,
            date_col='month',
            fill_col='user_count',
        )
        
        df_combined = pd.merge(
            patient_registration_history_df[['month', 'user_count']].rename(columns={'user_count': 'registration_count'}),
            paitent_deregistration_history_df[['month', 'user_count']].rename(columns={'user_count': 'deregistration_count'}),
            on='month',
            how='outer'
        ).fillna(0) 
        
        startrow_combined_data = 13
        df_combined = write_data_to_excel(
            df_combined, sheet_name, startrow_combined_data, 1, writer,
            'Patient Registration & Deregistration History',
            {'month': 'Month', 'registration_count': 'Registration Count', 'deregistration_count': 'Deregistration Count'}
        )
        patient_registration_chart = create_chart(
            workbook, 
            'column',
            'Patient Registration Count',
            sheet_name,
            start_row=13,
            start_col=1, 
            df_len=len(df_combined), 
            value_col=2,
        )
        worksheet.insert_chart('G3', patient_registration_chart)
        
        patient_deregistration_chart = create_chart(
            workbook,
            'column',
            'Patient Deregistration Count',
            sheet_name,
            start_row=13,
            start_col=1,
            df_len=len(df_combined),
            value_col=3,
        )
        
        worksheet.insert_chart('G20', patient_deregistration_chart)
        
        worksheet.set_column('D:D', 20,value_format) 
        worksheet.set_column('B:B', 20, value_format) 
        worksheet.set_column('C:C', 20, value_format)     
            
async def add_patient_demographics_data(basic_analytics: BasicAnalyticsStatistics, writer):
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
                df_age, sheet_name, start_row, start_col, writer,
                'Age Distribution',
                {'age_group': 'Age Group', 'count': 'Count'}
            )
            chart_age = create_chart(
                writer.book, 'pie', 'Age Distribution', sheet_name, start_row, start_col, len(df_age), value_col = start_col+1
            )
            worksheet.insert_chart(start_row, 4, chart_age)
            start_row += len(df_age) + 13  # Adjust start row for next section

        if patient_demographics.GenderGroups:
            df_gender = pd.DataFrame(patient_demographics.GenderGroups)
            df_gender = write_data_to_excel(
                df_gender, sheet_name, start_row, 1, writer,
                'Gender Distribution',
                {'gender': 'Gender', 'count': 'Count'}
            )
            chart_gender = create_chart(
                writer.book, 'pie', 'Gender Distribution', sheet_name, start_row, start_col, len(df_gender), value_col = start_col+1
            )
            worksheet.insert_chart(start_row, 4, chart_gender)
            start_row += len(df_gender) + 13

        if patient_demographics.EthnicityGroups:
            df_ethnicity = pd.DataFrame(patient_demographics.EthnicityGroups)
            df_ethnicity['ethnicity'] = df_ethnicity['ethnicity'].replace('', 'Unspecified').fillna('Unspecified')
            df_ethnicity = write_data_to_excel(
                df_ethnicity, sheet_name, start_row, start_col, writer,
                'Ethnicity Distribution',
                {'ethnicity': 'Ethnicity', 'count': 'Count'}
            )
            chart_ethnicity = create_chart(
                writer.book, 'pie', 'Ethnicity Distribution', sheet_name, start_row, 1, len(df_ethnicity), value_col = start_col+1
            )
            worksheet.insert_chart(start_row, 4, chart_ethnicity)
            start_row += len(df_ethnicity) + 13

        if patient_demographics.SurvivorOrCareGiverDistribution:
            df_survivor = pd.DataFrame(patient_demographics.SurvivorOrCareGiverDistribution)
            df_survivor = write_data_to_excel(
                df_survivor, sheet_name, start_row, start_col, writer,
                'Survivor/Caregiver Distribution',
                {'caregiver_status': 'Caregiver Status', 'count': 'Count'}
            )
            chart_survivor = create_chart(
                writer.book, 'pie', 'Survivor/Caregiver Distribution', sheet_name, start_row, start_col, len(df_survivor),value_col = start_col+1
            )
            worksheet.insert_chart(start_row, 4, chart_survivor)

        start_row = 3
        start_col = 13
        if patient_demographics.RaceGroups:
            df_race = pd.DataFrame(patient_demographics.RaceGroups)
            df_race['race'] = df_race['race'].replace('', 'Unspecified').fillna('Unspecified')
            df_race = write_data_to_excel(
                df_race, sheet_name, start_row, start_col, writer,
                'Race Distribution',
                {'race': 'Race', 'count': 'Count'}
            )
            chart_race = create_chart(
                writer.book, 'pie', 'Race Distribution', sheet_name, start_row, start_col, len(df_race), value_col = start_col+1
            )
            worksheet.insert_chart(start_row, start_col + 3, chart_race)
            start_row += len(df_race) + 13

        if patient_demographics.HealthSystemDistribution:
            df_health_system = pd.DataFrame(patient_demographics.HealthSystemDistribution)
            df_health_system = write_data_to_excel(
                df_health_system, sheet_name, start_row, start_col, writer,
                'Health System Distribution',
                {'health_system': 'Health System', 'count': 'Count'}
            )
            chart_health_system = create_chart(
                writer.book, 'pie', 'Health System Distribution', sheet_name, start_row, start_col, len(df_health_system), value_col = start_col+1
            )
            worksheet.insert_chart(start_row, start_col + 3, chart_health_system)
            start_row += len(df_health_system) + 13

        if patient_demographics.HospitalDistribution:
            df_hospital = pd.DataFrame(patient_demographics.HospitalDistribution)
            df_hospital = write_data_to_excel(
                df_hospital, sheet_name, start_row, start_col, writer,
                'Hospital Distribution',
                {'hospital': 'Hospital', 'count': 'Count'}
            )
            chart_hospital = create_chart(
                writer.book, 'pie', 'Hospital Distribution', sheet_name, start_row, start_col, len(df_hospital), value_col = start_col+1
            )
            worksheet.insert_chart(start_row, start_col + 3, chart_hospital)
            start_row += len(df_hospital) + 13

    except Exception as e:
        print(f"An error occurred: {e}")

#####################################################################################

async def add_active_users_data(generic_engagement_metrics: GenericEngagementMetrics, writer) -> None:
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
            daily_active_users_df = reindex_dataframe_to_all_dates(
                daily_active_users_df, 
                date_col='activity_date',
                fill_col= 'daily_active_users',
            )
            daily_active_users_df_ = write_data_to_excel(
                daily_active_users_df, sheet_name, start_row, col_daily, writer,
                'Daily Active Users',
                {'activity_date': 'Activity Date', 'daily_active_users': 'Daily Active Users'}
            )
            daily_active_users_chart = create_chart(writer.book, 'column', 'Daily Active Users', sheet_name, start_row, col_daily, len(daily_active_users_df_), value_col = col_daily+1)
            worksheet.insert_chart(start_row , col_monthly + 3, daily_active_users_chart)     

        if generic_engagement_metrics.WeeklyActiveUsers:
            weekly_active_users_df = pd.DataFrame(generic_engagement_metrics.WeeklyActiveUsers)
            weekly_active_users_df_ = write_data_to_excel(
                weekly_active_users_df, sheet_name, start_row, col_weekly, writer,'Weekly Active Users',
                {'week_start_date': 'Week Start Date', 'week_end_date': 'Week End Date', 'weekly_active_users': 'Weekly Active Users'}
            ) 
            
            weekly_active_users_chart = create_chart(
            writer.book,
            'column',
            'Weekly Active Users',
            sheet_name,
            start_row=start_row,
            start_col=col_weekly, 
            df_len=len(weekly_active_users_df_), 
            value_col=col_weekly + 2,
        )
        worksheet.insert_chart(start_row + 16, col_monthly + 3, weekly_active_users_chart)

        if generic_engagement_metrics.MonthlyActiveUsers:
            monthly_active_users_df = pd.DataFrame(generic_engagement_metrics.MonthlyActiveUsers)
            monthly_active_users_reindex = reindex_dataframe_to_all_months(
                monthly_active_users_df, 
                date_col='activity_month',
                fill_col= 'monthly_active_users',
            )
            monthly_active_users_df_ = write_data_to_excel(
                monthly_active_users_reindex, sheet_name, start_row, col_monthly, writer,
                'Monthly Active Users',
                {'activity_month': 'Activity Month', 'monthly_active_users': 'Monthly Active Users'}
            )
            monthly_active_users_chart = create_chart(writer.book, 'column', 'Monthly Active Users', sheet_name, start_row, col_monthly, len(monthly_active_users_df_), value_col = col_monthly+1)
            worksheet.insert_chart(start_row + 32, col_monthly + 3, monthly_active_users_chart)
        
    except Exception as e:
        print(f"An error occurred: {e}")

async def add_generic_engagement_data(generic_engagement_metrics: GenericEngagementMetrics, writer) -> None:
    try:
        
        start_row = 3
        col_login_freq = 1
        col_retention_days = 14
        col_retention_intervals = 18
        col_most_com_vis_features=32
        
        sheet_name = 'Generic Engagement'
        if sheet_name not in writer.sheets:
            worksheet = writer.book.add_worksheet(sheet_name)
        else:
            worksheet = writer.sheets[sheet_name]
        
        if generic_engagement_metrics.LoginFrequency:
            df_login_freq = pd.DataFrame(generic_engagement_metrics.LoginFrequency)  
            df_login_freq = write_data_to_excel(
                df_login_freq, 'Generic Engagement', start_row, col_login_freq, writer,
                'Login Frequency',
                {'month': 'Month', 'login_count': 'Login Count'}
            )
            chart_login_freq = create_chart(writer.book, 'column', 'Login Frequency', sheet_name, start_row, col_login_freq, len(df_login_freq), value_col=col_login_freq+1)
            worksheet.insert_chart(start_row , col_login_freq + 4, chart_login_freq)
    
            if generic_engagement_metrics.RetentionRateOnSpecificDays:
                retention_specific_days = generic_engagement_metrics.RetentionRateOnSpecificDays['retention_on_specific_days']
                retention_days_df = pd.DataFrame(retention_specific_days)
                retention_days_df_ = write_data_to_excel(
                    retention_days_df, sheet_name, start_row, col_retention_days, writer,
                    'Retention Rate on Specific Days',
                    {'day': 'Day', 'returning_users': 'Returning Users', 'retention_rate': 'Retention Rate'}
                )
                retention_rate_on_specific_days_chart = create_chart(writer.book, 'column', 'Retention Rate on Specific Days', sheet_name, start_row, col_retention_days, len(retention_days_df_), value_col = col_retention_days+2)
                worksheet.insert_chart(start_row, col_retention_intervals + 5, retention_rate_on_specific_days_chart)
        if generic_engagement_metrics.RetentionRateInSpecificIntervals:
            retention_intervals = generic_engagement_metrics.RetentionRateInSpecificIntervals['retention_in_specific_interval']
            retention_intervals_df = pd.DataFrame(retention_intervals)

            retention_intervals_df_ = write_data_to_excel(
                retention_intervals_df, sheet_name, start_row, col_retention_intervals, writer,
                'Retention Rate in Specific Intervals',
                {'interval': 'Interval', 'returning_users': 'Returning Users', 'retention_rate': 'Retention Rate'}
            )
            retention_intervals_chart = create_chart(writer.book, 'column', 'Retention Rate in Specific Intervals', sheet_name, start_row, col_retention_intervals, len(retention_intervals_df_), value_col = col_retention_intervals+2)
            worksheet.insert_chart(start_row + 18, col_retention_intervals + 5, retention_intervals_chart)

        if generic_engagement_metrics.MostCommonlyVisitedFeatures:
            most_commonly_visited_features_df = pd.DataFrame(generic_engagement_metrics.MostCommonlyVisitedFeatures)  
            most_commonly_visited_features_df_ = write_data_to_excel(
            most_commonly_visited_features_df, sheet_name, start_row, col_most_com_vis_features, writer,
                    'Most visited features',
                    {'month': 'Month','feature':'Feature', 'feature_usage_count': 'Feature Usage Count'}
                )
            most_commonly_visited_features_chart = writer.book.add_chart({'type': 'column'})
            most_commonly_visited_features_chart.add_series({
                'name': '',
                'categories': [sheet_name, start_row + 1, col_most_com_vis_features, start_row + len(most_commonly_visited_features_df_), col_most_com_vis_features],
                'values': [sheet_name, start_row + 1, col_most_com_vis_features + 2, start_row + len(most_commonly_visited_features_df_), col_most_com_vis_features + 2],
            })
            most_commonly_visited_features_chart.set_title({'name': 'Most visited features'})
            most_commonly_visited_features_chart.set_x_axis({
                'major_gridlines': {
                    'visible': True,
                    'line': {'color': '#CCCCCC', 'dash_type': 'dot','transparency': 0.8}
                }
                })
            most_commonly_visited_features_chart.set_y_axis({
                    'major_gridlines': {
                        'visible': True,
                        'line': {'color': '#CCCCCC', 'dash_type': 'dot','transparency': 0.8}
                    }
                })
            worksheet.insert_chart(start_row , col_most_com_vis_features + 5, most_commonly_visited_features_chart)
   
    except Exception as e:
        print(f"An error occurred: {e}")
        
################################################################################################

async def add_feature_engagement_data(feature_engagement_metrics: FeatureEngagementMetrics, writer):
    try:      
        start_row = 3
        col_access_frequency = 1 
        col_engagement_rate = 5 
        col_retention_days = 19
        col_retention_intervals = 23
        col_dopoff_points=38
        sheet_name = 'Medication Engagement'
        
        if sheet_name not in writer.sheets:
            worksheet = writer.book.add_worksheet(sheet_name)
        else:
            worksheet = writer.sheets[sheet_name]
            
        engagement_metrics = feature_engagement_metrics
        
        if feature_engagement_metrics.AccessFrequency:
            access_frequency_df = pd.DataFrame(feature_engagement_metrics.AccessFrequency) 
            access_frequency_reindex = reindex_dataframe_to_all_months(
                    access_frequency_df,
                    date_col='month',
                    fill_col='access_frequency',
                ) 
            access_frequency_df_=  write_data_to_excel(
                access_frequency_reindex, sheet_name, start_row, col_access_frequency, writer,
                'Access Frequency',
                {'month': 'Month', 'access_frequency': 'Access Frequency'}
            )
            access_frequency_chart = create_chart(writer.book, 'column', 'Access Frequency', 'Medication Engagement', start_row, col_access_frequency, len(access_frequency_df_), value_col = col_access_frequency+1)
            worksheet.insert_chart(start_row , col_engagement_rate + 5, access_frequency_chart)
        if engagement_metrics.EngagementRate:
                engagement_rate_df= pd.DataFrame(engagement_metrics.EngagementRate)
                engagement_rate_df['engagement_rate'] = pd.to_numeric(engagement_rate_df['engagement_rate'], errors='coerce')
                engagement_rate_df_ = reindex_dataframe_to_all_months(
                    engagement_rate_df,
                    date_col='month',
                    fill_col='engagement_rate',
                )
                engagement_rate_df =  write_data_to_excel(
                    engagement_rate_df_, 'Medication Engagement', start_row, col_engagement_rate, writer,
                    'Engagement Rate',
                    {'month': 'Month','feature':'Feature', 'engagement_rate': 'Engagement Rate'}
                )
                
                engagement_rate_chart = create_chart(writer.book, 'column', 'Engagement Rate', 'Medication Engagement', start_row, col_engagement_rate, len(engagement_rate_df), value_col = col_engagement_rate+2)
                worksheet.insert_chart(start_row + 18 , col_engagement_rate + 5, engagement_rate_chart)

        if engagement_metrics.RetentionRateOnSpecificDays:
            retention_specific_days = engagement_metrics.RetentionRateOnSpecificDays['retention_on_specific_days']
            retention_days_df= pd.DataFrame(retention_specific_days)
            retention_days_df_ = write_data_to_excel(
                retention_days_df, 'Medication Engagement', start_row, col_retention_days, writer,
                'Retention Rate on Specific Days',
                {'day': 'Day', 'returning_users': 'Returning Users', 'retention_rate': 'Retention Rate'}
            )
            retention_days_chart = create_chart(writer.book, 'column', 'Retention Rate on Specific Days', 'Medication Engagement', start_row, col_retention_days, len(retention_days_df_), value_col = col_retention_days+2)
            worksheet.insert_chart(start_row, col_retention_intervals + 5, retention_days_chart)

        if engagement_metrics.RetentionRateInSpecificIntervals:
            retention_intervals = engagement_metrics.RetentionRateInSpecificIntervals['retention_in_specific_interval']
            retention_intervals_df = pd.DataFrame(retention_intervals)

            retention_intervals_df_ = write_data_to_excel(
                retention_intervals_df, 'Medication Engagement', start_row, col_retention_intervals, writer,
                'Retention Rate in Specific Intervals',
                {'interval': 'Interval', 'returning_users': 'Returning Users', 'retention_rate': 'Retention Rate'}
            )
            retention_intervals_chart = create_chart(writer.book, 'column', 'Retention Rate in Specific Intervals', 'Medication Engagement', start_row, col_retention_intervals, len(retention_intervals_df_), value_col = col_retention_intervals+2)
            worksheet.insert_chart(start_row + 18, col_retention_intervals + 5, retention_intervals_chart)

        if engagement_metrics.DropOffPoints:
            drop_off_points_df = pd.DataFrame(engagement_metrics.DropOffPoints)
            drop_off_points_df['dropoff_rate'] = pd.to_numeric(drop_off_points_df['dropoff_rate'], errors='coerce')
            drop_off_points_df['dropoff_count'] = pd.to_numeric(drop_off_points_df['dropoff_count'], errors='coerce')
            drop_off_points_df_ = write_data_to_excel(
                drop_off_points_df, sheet_name, start_row, col_dopoff_points, writer,
                'Dropoff Points',
                {'event_name': 'Event Name', 'dropoff_count':'Dropoff Count','total_users':'Total Users', 'dropoff_rate': 'Dropoff Rate'}
            )
            drop_off_points_chart = create_chart(
                writer.book, 'pie', 'Dropoff Points', sheet_name, start_row, col_dopoff_points, len(drop_off_points_df_),value_col=col_dopoff_points+1
            )
            worksheet.insert_chart(start_row, col_dopoff_points + 5, drop_off_points_chart)
            
    except Exception as e:
        print(f"Error generating report: {e}")
        return ""