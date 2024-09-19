import pandas as pd
from app.database.services.analytics.reports.report_utilities import(
  create_chart,
  reindex_dataframe_to_all_missing_dates,
  write_data_to_excel
  )
from app.domain_types.schemas.analytics import FeatureEngagementMetrics

####################################################################################

async def feature_engagement(feature_feature_engagement_metrics: FeatureEngagementMetrics, writer, sheet_name:str):
    try:      
        start_row = 3
        col_access_frequency = 1 
        col_engagement_rate = 5 
        col_retention_days = 19
        col_retention_intervals = 23
        col_dopoff_points = 38
        
        sheet_name = sheet_name
        
        if sheet_name not in writer.sheets:
            worksheet = writer.book.add_worksheet(sheet_name)
        else:
            worksheet = writer.sheets[sheet_name]
        
        if feature_feature_engagement_metrics.AccessFrequency:
            access_frequency_df = pd.DataFrame(feature_feature_engagement_metrics.AccessFrequency) 
            access_frequency_reindex = reindex_dataframe_to_all_missing_dates(
                    data_frame = access_frequency_df,
                    date_col = 'month',
                    fill_col = 'access_frequency',
                ) 
            access_frequency_df_=  write_data_to_excel(
                data_frame = access_frequency_reindex,
                sheet_name = sheet_name,
                start_row = start_row,
                start_col = col_access_frequency,
                writer = writer,
                title = 'Access Frequency',
               rename_columns = {'month': 'Month', 'access_frequency': 'Access Frequency'}
            )
            access_frequency_chart = create_chart(
                workbook = writer.book, 
                chart_type = 'column', 
                series_name = 'Access Frequency', 
                sheet_name = sheet_name, 
                start_row = start_row,
                start_col = col_access_frequency, 
                df_len = len(access_frequency_df_), 
                value_col = col_access_frequency+1)
            worksheet.insert_chart(start_row , col_engagement_rate + 5, access_frequency_chart)
            
        if feature_feature_engagement_metrics.EngagementRate:
                engagement_rate_df= pd.DataFrame(feature_feature_engagement_metrics.EngagementRate)
                engagement_rate_df['engagement_rate'] = pd.to_numeric(engagement_rate_df['engagement_rate'], errors='coerce')
                engagement_rate_df_ = reindex_dataframe_to_all_missing_dates(
                    data_frame = engagement_rate_df,
                    date_col = 'month',
                    fill_col = 'engagement_rate',
                )
                engagement_rate_df =  write_data_to_excel(
                    data_frame = engagement_rate_df_,
                    sheet_name = sheet_name,
                    start_row = start_row,
                    start_col = col_engagement_rate,
                    writer = writer,
                    title = 'Engagement Rate',
                    rename_columns = {'month': 'Month','feature':'Feature', 'engagement_rate': 'Engagement Rate'}
                )     
                engagement_rate_chart = create_chart(
                    workbook = writer.book,
                    chart_type = 'column',
                    series_name = 'Engagement Rate',
                    sheet_name = sheet_name,
                    start_row = start_row,
                    start_col = col_engagement_rate,
                    df_len = len(engagement_rate_df),
                    value_col = col_engagement_rate + 2
                )
                worksheet.insert_chart(start_row + 18 , col_engagement_rate + 5, engagement_rate_chart)

        if feature_feature_engagement_metrics.RetentionRateOnSpecificDays:
            retention_specific_days = feature_feature_engagement_metrics.RetentionRateOnSpecificDays['retention_on_specific_days']
            retention_days_df= pd.DataFrame(retention_specific_days)
            retention_days_df_ = write_data_to_excel(
                data_frame = retention_days_df,
                sheet_name = sheet_name,
                start_row = start_row,
                start_col = col_retention_days,
                writer = writer,
                title = 'Retention Rate on Specific Days',
                rename_columns = {'day': 'Day', 'returning_users': 'Returning Users', 'retention_rate': 'Retention Rate'}
            )
            retention_days_chart = create_chart(
                workbook = writer.book,
                chart_type = 'column',
                series_name = 'Retention Rate on Specific Days', 
                sheet_name = sheet_name,
                start_row = start_row,
                start_col = col_retention_days,
                df_len = len(retention_days_df_),
                value_col = col_retention_days + 2
            )
            worksheet.insert_chart(start_row, col_retention_intervals + 5, retention_days_chart)

        if feature_feature_engagement_metrics.RetentionRateInSpecificIntervals:
            retention_intervals = feature_feature_engagement_metrics.RetentionRateInSpecificIntervals['retention_in_specific_interval']
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
               workbook = writer.book,
                chart_type = 'column',
                series_name = 'Retention Rate in Specific Intervals',
                sheet_name = sheet_name,
                start_row = start_row,
                start_col = col_retention_intervals,
                df_len = len(retention_intervals_df_),
                value_col = col_retention_intervals + 2
            )
            worksheet.insert_chart(start_row + 18, col_retention_intervals + 5, retention_intervals_chart)

        if feature_feature_engagement_metrics.DropOffPoints:
            drop_off_points_df = pd.DataFrame(feature_feature_engagement_metrics.DropOffPoints)
            drop_off_points_df['dropoff_rate'] = pd.to_numeric(drop_off_points_df['dropoff_rate'], errors='coerce')
            drop_off_points_df['dropoff_count'] = pd.to_numeric(drop_off_points_df['dropoff_count'], errors='coerce')
            drop_off_points_df_ = write_data_to_excel(
                data_frame = drop_off_points_df,
                sheet_name = sheet_name,
                start_row = start_row,
                start_col = col_dopoff_points,
                writer = writer,
                title = 'Dropoff Points',
                rename_columns = {'event_name': 'Event Name', 'dropoff_count':'Dropoff Count','total_users':'Total Users', 'dropoff_rate': 'Dropoff Rate'}
            )
            drop_off_points_chart = create_chart(
                workbook = writer.book,
                chart_type = 'pie',
                series_name = 'Dropoff Points',
                sheet_name = sheet_name,
                start_row = start_row,
                start_col = col_dopoff_points,
                df_len = len(drop_off_points_df_),
                value_col = col_dopoff_points + 1
            )
            worksheet.insert_chart(start_row, col_dopoff_points + 5, drop_off_points_chart)
            
    except Exception as e:
        print(f"Error generating report: {e}")
        return ""