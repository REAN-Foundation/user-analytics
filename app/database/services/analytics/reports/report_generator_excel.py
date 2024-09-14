
# from datetime import datetime
# import json
# import os
# from app.database.services.analytics.common import get_report_folder_path
# from app.domain_types.schemas.analytics import GenericEngagementMetrics
# import pandas as pd

# ###############################################################################

# async def generate_user_engagement_report_excel(
#         analysis_code: str, user_engagement_metrics: GenericEngagementMetrics) -> str:
#     try:
#        excel_file_path = os.path.join(reports_path, f"user_engagement_report_{analysis_code}.xlsx")
#         with pd.ExcelWriter(excel_file_path) as writer:
#             await add_daily_active_users(user_engagement_metrics.DailyActiveUsers, writer)
#             await add_weekly_active_users(user_engagement_metrics.WeeklyActiveUsers, writer)
#         return excel_file_path
#     except Exception as e:
#         print(e)
#         return ""  reports_path = get_report_folder_path()
#        

# ###############################################################################

# async def add_daily_active_users(daily_active_users: list|None, writer) -> None:
#     try:
#         if daily_active_users:
#             df = pd.DataFrame(daily_active_users)
#             df.to_excel(writer, sheet_name='Daily Active Users', index=False)
#             # Access the xlsxwriter workbook and worksheet objects
#             workbook = writer.book
#             worksheet = writer.sheets["Daily Active Users"]
#             worksheet.conditional_format(1, 2, len(df), 2,
#                              {'type': '3_color_scale'})
#             # Create a chart object (Line chart for example)
#             chart = workbook.add_chart({'type': 'column'})

#             # Define the range for the chart data
#             # First column -> Date
#             # Second column -> Daily Active Users
#             chart.add_series({
#                 'name': 'Daily Active Users',
#                 'categories': ['Daily Active Users', 1, 0, len(df), 0],  # Date range
#                 'values': ['Daily Active Users', 1, 1, len(df), 1],      # Active users range
#             })

#             # Add chart title and labels
#             chart.set_title({'name': 'Daily Active Users Over Time'})
#             chart.set_x_axis({'name': 'Date'})
#             chart.set_y_axis({'name': 'Active Users'})

#             # Insert the chart into the worksheet
#             worksheet.insert_chart('E2', chart)

#     except Exception as e:
#         print(e)

# async def add_weekly_active_users(weekly_active_users: list|None, writer) -> None:
    # try:
    #     if weekly_active_users:
    #         df = pd.DataFrame(weekly_active_users)
    #         df.to_excel(writer, sheet_name='Weekly Active Users', index=False)
    #         # Access the xlsxwriter workbook and worksheet objects
    #         workbook = writer.book
    #         worksheet = writer.sheets["Weekly Active Users"]
    #         worksheet.conditional_format(1, 2, len(df), 2,
    #                          {'type': '3_color_scale'})
    #         # Create a chart object (Line chart for example)
    #         chart = workbook.add_chart({'type': 'column'})

    #         # Define the range for the chart data
    #         # First column -> Date
    #         # Second column -> Weekly Active Users
    #         chart.add_series({
    #             'name': 'Weekly Active Users',
    #             'categories': ['Weekly Active Users', 1, 0, len(df), 0],  # Date range
    #             'values': ['Weekly Active Users', 1, 1, len(df), 1],      # Active users range
    #         })

    #         # Add chart title and labels
    #         chart.set_title({'name': 'Weekly Active Users Over Time'})
    #         chart.set_x_axis({'name': 'Date'})
    #         chart.set_y_axis({'name': 'Active Users'})

    #         # Insert the chart into the worksheet
    #         worksheet.insert_chart('E2', chart)

    # except Exception as e:
    #     print(e)

import os
import json
import pandas as pd
from datetime import datetime
from app.domain_types.schemas.analytics import BasicAnalyticsStatistics, EngagementMetrics, FeatureEngagementMetrics, GenericEngagementMetrics

# Function to get report folder path
def get_report_folder_path() -> str:
    cwd = os.getcwd()
    today = datetime.today()
    date_timestamp = today.strftime("%Y%m%d")
    reports_path = os.path.join(cwd, 'tmp', 'analytics_reports', date_timestamp)
    os.makedirs(reports_path, exist_ok=True)
    return reports_path

# Function to read JSON data from file
def read_json_file(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        data = json.load(file)
        print("data",data)
    return data

# This fuction is for adding the missing month and make count 0
def reindex_dataframe_to_all_months(df, date_col, fill_col, fill_value=0, date_format='%Y-%m'):

    # Convert the date column to datetime format
    df[date_col] = pd.to_datetime(df[date_col], format=date_format)
    
    # Get the range of dates from the minimum to maximum date
    start_date = df[date_col].min()
    end_date = df[date_col].max()
    all_dates = pd.date_range(start=start_date, end=end_date, freq='MS')
    
    # Create a DataFrame with all months
    all_dates_df = pd.DataFrame({date_col: all_dates})
    
    # Merge and fill missing values with the specified fill value
    df_reindexed = pd.merge(all_dates_df, df, on=date_col, how='left').fillna({fill_col: fill_value})

     # Format the date column to 'YYYY-MM' to display only year and month
    df_reindexed[date_col] = df_reindexed[date_col].dt.strftime('%Y-%m')

    return df_reindexed

def write_data_to_excel(df, sheet_name: str, start_row: int, start_col: int, writer, title: str, rename_columns=None):
    title_format = writer.book.add_format({'bold': True, 'font_size': 14, 'align': 'left', 'valign': 'vcenter'})
    worksheet = writer.sheets[sheet_name]
    
    # Write the title before data
    worksheet.write(start_row - 1, start_col, title, title_format)
    
    # Rename columns if specified
    if rename_columns:
        df.rename(columns=rename_columns, inplace=True)
    
    df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=start_row, startcol=start_col,)
    
    # Dynamically adjust column width without padding
    for i, col in enumerate(df.columns):
        max_len = max(df[col].astype(str).map(len).max(), len(col))  # No additional padding
        worksheet.set_column(start_col + i, start_col + i, max_len)
    
    return df

def create_chart(workbook, chart_type, series_name, sheet_name, start_row, start_col, df_len, x_axis= '' , y_axis = ''):
    chart = workbook.add_chart({'type': chart_type})
    chart.add_series({
        'name': series_name,
        'categories': [sheet_name, start_row + 1, start_col, start_row + df_len, start_col],
        'values': [sheet_name, start_row + 1, start_col + 1, start_row + df_len, start_col + 1],
    })
    chart.set_title({'name': f'{series_name}'})
    chart.set_x_axis({'name': x_axis})
    chart.set_y_axis({'name': y_axis})
    return chart

#####################################################################
      
async def generate_user_engagement_report_excel() -> str:
    try:
        # Example analysis code
        analysis_code = '28'

        # Load JSON data from the file for basic analytics
        basic_analysis_data_path = 'test_data/basic_statistic.json'
        basic_analysis_data = read_json_file(basic_analysis_data_path)
         
        # Load JSON data for generic engagement metrics
        generic_engagement_metrics_data_path = 'test_data/generic_engagement_metrics.json'
        generic_engagement_metrics_data = read_json_file(generic_engagement_metrics_data_path)
          
        # Load JSON data for feature engagement metrics
        feature_engagement_data_path = 'test_data/feature_engagement_metrics_medication.json'
        feature_engagement_data = read_json_file(feature_engagement_data_path)

        # Initialize the loaded data
        basic_analysis = BasicAnalyticsStatistics(**basic_analysis_data)
        generic_engagement_metrics = GenericEngagementMetrics(**generic_engagement_metrics_data)
        feature_engagement_metrics = FeatureEngagementMetrics(**feature_engagement_data)
       
        reports_path = get_report_folder_path()
        excel_file_path = os.path.join(reports_path, f"user_engagement_report_{analysis_code}.xlsx")
        with pd.ExcelWriter(excel_file_path, engine='xlsxwriter') as writer:
             await add_basic_analytics_statistics(basic_analysis, writer) 
             await add_patient_demographics_data(basic_analysis, writer) 
             await add_generic_engagement_data(generic_engagement_metrics, writer)
            #  await add_feature_engagement_data(feature_engagement_metrics, writer)
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
  
    sheet_name = 'Basic Analytics Statistics'
    df_stats.to_excel(writer, sheet_name=sheet_name, index=False, startrow=2, startcol=1)
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]

    # Define formats
    title_format = workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center', 'valign': 'vcenter'})
    field_bold_format = workbook.add_format({'bold': True, 'align': 'left'})  # Format for making Property column bold
    value_format = workbook.add_format({'align': 'left'})

    # Apply bold format to the "Property" column and value format to the "Value" column
    for row_num in range(len(df_stats)):
        worksheet.write(row_num + 2, 1, df_stats.at[row_num, 'Property'], field_bold_format)  # Make Property column bold
        worksheet.write(row_num + 2, 2, df_stats.at[row_num, 'Value'], value_format)

    # Add title
    worksheet.merge_range('B1:C1', 'Basic Statistics', title_format)
    
    # # Set column widths for better readability
    worksheet.set_column('B:B', 20) 
    worksheet.set_column('C:C', 15) 

    if basic_analytics.PatientRegistrationHistory:
        
        df_patient_registration_ = pd.DataFrame(basic_analytics.PatientRegistrationHistory)
        df_patient_registration = reindex_dataframe_to_all_months(
            df_patient_registration_,
            date_col='month',
            fill_col='user_count',
        )
        # Write Patient Registration History
        startrow_patient_data = 13
        df_patient_registration = write_data_to_excel(
                df_patient_registration, sheet_name, startrow_patient_data, 1, writer,
                'Patient Registration History',
                {'month': 'Month', 'user_count': 'User Count'}
            )
        chart = workbook.add_chart({'type': 'column'})
        chart.add_series({
            'name': 'User Count',
            'categories': [sheet_name, startrow_patient_data + 1, 1, startrow_patient_data + len(df_patient_registration), 1],  # Adjusted categories
            'values': [sheet_name, startrow_patient_data + 1, 2, startrow_patient_data + len(df_patient_registration), 2],  # Adjusted values
        })
        
        chart.set_title({'name': 'Patient Registration History'})
        chart.set_x_axis({'name': 'Month'})
        chart.set_y_axis({'name': 'User Count'})
        
        worksheet.insert_chart('E17', chart)  
        
    if basic_analytics.PatientDeregistrationHistory:
        df_dereg_history_ = pd.DataFrame(basic_analytics.PatientDeregistrationHistory)
        df_dereg_history = reindex_dataframe_to_all_months(
            df_dereg_history_,
            date_col='month',
            fill_col='user_count',
        )
        startrow_dereg_data = 13
        df_dereg_history = write_data_to_excel(
                df_dereg_history, sheet_name, startrow_dereg_data, 13, writer,
                'Patient Deregistration History',
                {'month': 'Month', 'user_count': 'User Count'}
            )
        chart = workbook.add_chart({'type': 'column'})
        
        chart.add_series({
            'name': 'User Count',
            'categories': [sheet_name, startrow_dereg_data + 1, 13, startrow_dereg_data + len(df_dereg_history), 13],  # Adjusted categories
            'values': [sheet_name, startrow_dereg_data + 1, 14, startrow_dereg_data + len(df_dereg_history), 14],  # Adjusted values
        })
        
        chart.set_title({'name': 'Patient Deregistration History'})
        chart.set_x_axis({'name': 'Month'})
        chart.set_y_axis({'name': 'User Count'})
        
        worksheet.insert_chart('R17', chart)      
            
async def add_patient_demographics_data(basic_analytics: BasicAnalyticsStatistics, writer):
    try:
        sheet_name = 'Patient Demographics'
        if sheet_name not in writer.sheets:
            worksheet = writer.book.add_worksheet(sheet_name)
        else:
            worksheet = writer.sheets[sheet_name]

        # Add the title at the top of the sheet
        title = "Patient Demographic Report"
        worksheet.merge_range('A1:Z1', title, writer.book.add_format({'bold': True, 'font_size': 16, 'align': 'center'}))

        patient_demographics = basic_analytics.PatientDemographics

        # Part 1: Age, Gender, Ethnicity Groups
        start_row = 3
        if patient_demographics.AgeGroups:
            df_age = pd.DataFrame(patient_demographics.AgeGroups)
            df_age = write_data_to_excel(
                df_age, sheet_name, start_row, 1, writer,
                'Age Distribution',
                {'age_group': 'Age Group', 'count': 'Count'}
            )
            chart_age = create_chart(
                writer.book, 'pie', 'Age Distribution', sheet_name, start_row, 1, len(df_age)
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
                writer.book, 'pie', 'Gender Distribution', sheet_name, start_row, 1, len(df_gender)
            )
            worksheet.insert_chart(start_row, 4, chart_gender)
            start_row += len(df_gender) + 13

        if patient_demographics.EthnicityGroups:
            df_ethnicity = pd.DataFrame(patient_demographics.EthnicityGroups)
            df_ethnicity['ethnicity'] = df_ethnicity['ethnicity'].replace('', 'Unspecified').fillna('Unspecified')
            df_ethnicity = write_data_to_excel(
                df_ethnicity, sheet_name, start_row, 1, writer,
                'Ethnicity Distribution',
                {'ethnicity': 'Ethnicity', 'count': 'Count'}
            )
            chart_ethnicity = create_chart(
                writer.book, 'pie', 'Ethnicity Distribution', sheet_name, start_row, 1, len(df_ethnicity)
            )
            worksheet.insert_chart(start_row, 4, chart_ethnicity)
            start_row += len(df_ethnicity) + 13
            
        if patient_demographics.LocationGroups:
            df_location = pd.DataFrame(patient_demographics.LocationGroups)
            df_location = write_data_to_excel(
                df_location, sheet_name, start_row, 1, writer,
                'Location Distribution',
                {'Location': 'location', 'count': 'Count'}
            )
            chart_location = create_chart(
                writer.book, 'pie', 'Location Distribution', sheet_name, start_row, 1, len(df_location)
            )
            worksheet.insert_chart(start_row, 4, chart_location)
            start_row += len(df_location) + 13

        # Part 2: Race, Health System, Hospital, Survivor/Caregiver Distributions
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
                writer.book, 'pie', 'Race Distribution', sheet_name, start_row, start_col, len(df_race)
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
                writer.book, 'pie', 'Health System Distribution', sheet_name, start_row, start_col, len(df_health_system)
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
                writer.book, 'pie', 'Hospital Distribution', sheet_name, start_row, start_col, len(df_hospital)
            )
            worksheet.insert_chart(start_row, start_col + 3, chart_hospital)
            start_row += len(df_hospital) + 13

        if patient_demographics.SurvivorOrCareGiverDistribution:
            df_survivor = pd.DataFrame(patient_demographics.SurvivorOrCareGiverDistribution)
            df_survivor = write_data_to_excel(
                df_survivor, sheet_name, start_row, start_col, writer,
                'Survivor/Caregiver Distribution',
                {'caregiver_status': 'Caregiver Status', 'count': 'Count'}
            )
            chart_survivor = create_chart(
                writer.book, 'pie', 'Survivor/Caregiver Distribution', sheet_name, start_row, start_col, len(df_survivor)
            )
            worksheet.insert_chart(start_row, start_col + 4, chart_survivor)
    except Exception as e:
        print(f"An error occurred: {e}")

#####################################################################################

async def add_generic_engagement_data(generic_engagement_metrics: GenericEngagementMetrics, writer) -> None:
    try:
        start_row = 3
        col_daily = 1 
        col_weekly = 4 
        col_monthly = 8
        col_login_freq = 20
        col_stickiness = 23 
        col_retention_days = 36
        col_retention_intervals = 40
        
        sheet_name = 'Generic Engagement'
        if sheet_name not in writer.sheets:
            worksheet = writer.book.add_worksheet(sheet_name)
        else:
            worksheet = writer.sheets[sheet_name]
        
        # Write Daily Active Users data to Excel
        if generic_engagement_metrics.DailyActiveUsers:
            df_daily_active_users = pd.DataFrame(generic_engagement_metrics.DailyActiveUsers)
            df_daily_active_users = write_data_to_excel(
                df_daily_active_users, 'Generic Engagement', start_row, col_daily, writer,
                'Daily Active Users',
                {'activity_date': 'Activity Date', 'daily_active_users': 'Daily Active Users'}
            )
            chart_daily_active_users = create_chart(writer.book, 'column', 'Daily Active Users', 'Generic Engagement', start_row, col_daily, len(df_daily_active_users), 'Date', 'Active Users')
            worksheet.insert_chart(start_row , col_monthly + 3, chart_daily_active_users)     

        # # Write Weekly Active Users data to Excel
        if generic_engagement_metrics.WeeklyActiveUsers:
            df_weekly_active_users = pd.DataFrame(generic_engagement_metrics.WeeklyActiveUsers)
            df_weekly_active_users = write_data_to_excel(
                df_weekly_active_users, 'Generic Engagement', start_row, col_weekly, writer,'Weekly Active Users',
                {'week_start_date': 'Week Start Date', 'week_end_date': 'Week End Date', 'weekly_active_users': 'Weekly Active Users'}
            ) 
            chart_weekly_active_users = writer.book.add_chart({'type': 'column'})
            chart_weekly_active_users.add_series({
            'name': 'Weekly Active Users',
            'categories': ['Generic Engagement', start_row + 1, col_weekly, start_row + 1 + len(df_weekly_active_users) - 1, col_weekly],  # X-axis (Week Start Date)
            'values': ['Generic Engagement', start_row + 1, col_weekly + 2, start_row + 1 + len(df_weekly_active_users) - 1, col_weekly + 2],  # Y-axis (Weekly Active Users)
            })
        
            chart_weekly_active_users.set_title({'name': 'Weekly Active Users'})
            chart_weekly_active_users.set_x_axis({'name': 'Date'})
            chart_weekly_active_users.set_y_axis({'name': 'Active Users'})
            worksheet.insert_chart(start_row + 16, col_monthly + 3, chart_weekly_active_users)

        # Write Monthly Active Users data to Excel
        if generic_engagement_metrics.MonthlyActiveUsers:
            df_monthly_active_users_ = pd.DataFrame(generic_engagement_metrics.MonthlyActiveUsers)
            df_monthly_active_users = reindex_dataframe_to_all_months(
                df_monthly_active_users_, 
                date_col='activity_month',
                fill_col= 'monthly_active_users',
            )
            df_monthly_active_users = write_data_to_excel(
                df_monthly_active_users, 'Generic Engagement', start_row, col_monthly, writer,
                'Monthly Active Users',
                {'activity_month': 'Activity Month', 'monthly_active_users': 'Monthly Active Users'}
            )
            chart_monthly_active_users = create_chart(writer.book, 'column', 'Monthly Active Users', 'Generic Engagement', start_row, col_monthly, len(df_monthly_active_users), 'Date', 'Active Users')
            worksheet.insert_chart(start_row + 32, col_monthly + 3, chart_monthly_active_users)
        
        if generic_engagement_metrics.LoginFrequency:
            df_login_freq = pd.DataFrame(generic_engagement_metrics.LoginFrequency)  
            df_login_freq = write_data_to_excel(
                df_login_freq, 'Generic Engagement', start_row, col_login_freq, writer,
                'Login Frequency',
                {'month': 'Month', 'login_count': 'Login Count'}
            )
            chart_login_freq = create_chart(writer.book, 'column', 'Login Frequency', 'Generic Engagement', start_row, col_login_freq, len(df_login_freq), 'Date', 'Login Count')
            worksheet.insert_chart(start_row , col_stickiness + 5, chart_login_freq)
    
        if generic_engagement_metrics.StickinessRatio:
            df_stickiness_ratio = pd.DataFrame(generic_engagement_metrics.StickinessRatio)
            df_stickiness_ratio = write_data_to_excel(
                df_stickiness_ratio, 'Generic Engagement', start_row, col_stickiness, writer,
                'Stickiness Ratio',
                {'month': 'Month', 'avg_dau': 'Average DAU', 'mau': 'MAU', 'stickiness': 'Stickiness (%)'}
            )
            chart_stickiness_ratio = create_chart(writer.book, 'pie', 'Stickiness Ratio', 'Generic Engagement', start_row, col_stickiness, len(df_stickiness_ratio))
            worksheet.insert_chart(start_row + 16, col_stickiness + 5, chart_stickiness_ratio)
            
        if generic_engagement_metrics.RetentionRateOnSpecificDays:
            retention_specific_days = generic_engagement_metrics.RetentionRateOnSpecificDays['retention_on_specific_days']
            df_retention_days = pd.DataFrame(retention_specific_days)
            df_retention_days = write_data_to_excel(
                df_retention_days, 'Generic Engagement', start_row, col_retention_days, writer,
                'Retention Rate on Specific Days',
                {'day': 'Day', 'returning_users': 'Returning Users', 'retention_rate': 'Retention Rate'}
            )
            chart_retention_days = writer.book.add_chart({'type': 'column'})
            chart_retention_days.add_series({
                'name': 'Retention Rate',
                'categories': [sheet_name, start_row + 1, col_retention_days, start_row + len(df_retention_days), col_retention_days],
                'values': [sheet_name, start_row + 1, col_retention_days + 2, start_row + len(df_retention_days), col_retention_days + 2],
            })
            chart_retention_days.set_title({'name': 'Retention Rate on Specific Days'})
            chart_retention_days.set_x_axis({'name': 'Day'})
            chart_retention_days.set_y_axis({'name': 'Retention Rate'})
            worksheet.insert_chart(start_row, col_retention_intervals + 5, chart_retention_days)
            
        if generic_engagement_metrics.RetentionRateInSpecificIntervals:
            retention_intervals = generic_engagement_metrics.RetentionRateInSpecificIntervals['retention_in_specific_interval']
            df_retention_intervals = pd.DataFrame(retention_intervals)

            df_retention_intervals = write_data_to_excel(
                df_retention_intervals, 'Generic Engagement', start_row, col_retention_intervals, writer,
                'Retention Rate in Specific Intervals',
                {'interval': 'Interval', 'returning_users': 'Returning Users', 'retention_rate': 'Retention Rate'}
            )

            chart_retention_intervals = writer.book.add_chart({'type': 'column'})
            chart_retention_intervals.add_series({
                'name': 'Retention Rate',
                'categories': [sheet_name, start_row + 1, col_retention_intervals, start_row + len(df_retention_intervals), col_retention_intervals],
                'values': [sheet_name, start_row + 1, col_retention_intervals + 2, start_row + len(df_retention_intervals), col_retention_intervals + 2],
            })
            chart_retention_intervals.set_title({'name': 'Retention Rate in Specific Intervals'})
            chart_retention_intervals.set_x_axis({'name': 'Interval'})
            chart_retention_intervals.set_y_axis({'name': 'Retention Rate'})

            worksheet.insert_chart(start_row + 16, col_retention_intervals + 5, chart_retention_intervals)
        
    except Exception as e:
        print(f"An error occurred: {e}")
        
################################################################################################

async def add_feature_engagement_data(feature_engagement_metrics: FeatureEngagementMetrics, writer):
    try:      
        sheet_name = 'Feature Engagement-Medication'
        if sheet_name not in writer.sheets:
            worksheet = writer.book.add_worksheet(sheet_name)
        else:
            worksheet = writer.sheets[sheet_name]
        
            if feature_engagement_metrics.AccessFrequency:
                df_access_frequency = pd.DataFrame(feature_engagement_metrics.AccessFrequency)
                await write_data_to_excel(df_access_frequency, sheet_name, 2, 1, writer, 'Access Frequency', {'month': 'Month', 'access_frequency': 'Access Frequency'})
                chart_access = create_chart(writer.book, 'line', 'Access Frequency', sheet_name, 2, 1, len(df_access_frequency))
                worksheet.insert_chart('H3', chart_access)

            # Write "Engagement Rate" data
            
            if feature_engagement_metrics.EngagementRate:
                df_engagement_rate = pd.DataFrame(feature_engagement_metrics.EngagementRate)
                await write_data_to_excel(df_engagement_rate, sheet_name, 20, 1, writer, 'Engagement Rate', {'month': 'Month', 'engagement_rate': 'Engagement Rate'})
                chart_engagement_rate = create_chart(writer.book, 'line', 'Engagement Rate', sheet_name, 20, 1, len(df_engagement_rate))
                worksheet.insert_chart('H15', chart_engagement_rate)

          # Write "Retention Rate on Specific Days" data
            if feature_engagement_metrics.RetentionRateOnSpecificDays:
                df_retention_days = pd.DataFrame(feature_engagement_metrics.RetentionRateOnSpecificDays)
                await write_data_to_excel(df_retention_days, sheet_name, 40, 1, writer, 'Retention Rate on Specific Days', {'day': 'Day', 'returning_users': 'Returning Users', 'retention_rate': 'Retention Rate'})
                chart_retention_days = create_chart(writer.book, 'line', 'Retention Rate on Specific Days', sheet_name, 40, 1, len(df_retention_days))
                worksheet.insert_chart('H27', chart_retention_days)

            # Write "Retention Rate in Specific Intervals" data
            if feature_engagement_metrics.RetentionRateInSpecificIntervals:
                df_retention_intervals = pd.DataFrame(feature_engagement_metrics.RetentionRateInSpecificIntervals)
                await write_data_to_excel(df_retention_intervals, sheet_name, 60, 1, writer, 'Retention Rate in Specific Intervals', {'interval': 'Interval', 'returning_users': 'Returning Users', 'retention_rate': 'Retention Rate'})
                chart_retention_intervals = create_chart(writer.book, 'line', 'Retention Rate in Specific Intervals', sheet_name, 60, 1, len(df_retention_intervals))
                worksheet.insert_chart('H39', chart_retention_intervals)

            # Write "Drop-Off Points" data
            if feature_engagement_metrics.DropOffPoints:
                df_drop_off = pd.DataFrame(feature_engagement_metrics.DropOffPoints)
                await write_data_to_excel(df_drop_off, sheet_name, 80, 1, writer, 'Drop-Off Points', {'event_name': 'Event Name', 'dropoff_count': 'Dropoff Count', 'total_users': 'Total Users', 'dropoff_rate': 'Dropoff Rate'})
                chart_drop_off = create_chart(writer.book, 'column', 'Drop-Off Points', sheet_name, 80, 1, len(df_drop_off))
                worksheet.insert_chart('H51', chart_drop_off)

    except Exception as e:
        print(f"Error generating report: {e}")
        return ""
                