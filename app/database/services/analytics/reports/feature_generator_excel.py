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
        col_dopoff_points=38
        
        sheet_name = sheet_name
        
        if sheet_name not in writer.sheets:
            worksheet = writer.book.add_worksheet(sheet_name)
        else:
            worksheet = writer.sheets[sheet_name]
        
        if feature_feature_engagement_metrics.AccessFrequency:
            access_frequency_df = pd.DataFrame(feature_feature_engagement_metrics.AccessFrequency) 
            access_frequency_reindex = reindex_dataframe_to_all_missing_dates(
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
        if feature_feature_engagement_metrics.EngagementRate:
                engagement_rate_df= pd.DataFrame(feature_feature_engagement_metrics.EngagementRate)
                engagement_rate_df['engagement_rate'] = pd.to_numeric(engagement_rate_df['engagement_rate'], errors='coerce')
                engagement_rate_df_ = reindex_dataframe_to_all_missing_dates(
                    engagement_rate_df,
                    date_col='month',
                    fill_col='engagement_rate',
                )
                engagement_rate_df =  write_data_to_excel(
                    engagement_rate_df_, sheet_name, start_row, col_engagement_rate, writer,
                    'Engagement Rate',
                    {'month': 'Month','feature':'Feature', 'engagement_rate': 'Engagement Rate'}
                )
                
                engagement_rate_chart = create_chart(writer.book, 'column', 'Engagement Rate', sheet_name, start_row, col_engagement_rate, len(engagement_rate_df), value_col = col_engagement_rate+2)
                worksheet.insert_chart(start_row + 18 , col_engagement_rate + 5, engagement_rate_chart)

        if feature_feature_engagement_metrics.RetentionRateOnSpecificDays:
            retention_specific_days = feature_feature_engagement_metrics.RetentionRateOnSpecificDays['retention_on_specific_days']
            retention_days_df= pd.DataFrame(retention_specific_days)
            retention_days_df_ = write_data_to_excel(
                retention_days_df, sheet_name, start_row, col_retention_days, writer,
                'Retention Rate on Specific Days',
                {'day': 'Day', 'returning_users': 'Returning Users', 'retention_rate': 'Retention Rate'}
            )
            retention_days_chart = create_chart(writer.book, 'column', 'Retention Rate on Specific Days', sheet_name, start_row, col_retention_days, len(retention_days_df_), value_col = col_retention_days+2)
            worksheet.insert_chart(start_row, col_retention_intervals + 5, retention_days_chart)

        if feature_feature_engagement_metrics.RetentionRateInSpecificIntervals:
            retention_intervals = feature_feature_engagement_metrics.RetentionRateInSpecificIntervals['retention_in_specific_interval']
            retention_intervals_df = pd.DataFrame(retention_intervals)

            retention_intervals_df_ = write_data_to_excel(
                retention_intervals_df, sheet_name, start_row, col_retention_intervals, writer,
                'Retention Rate in Specific Intervals',
                {'interval': 'Interval', 'returning_users': 'Returning Users', 'retention_rate': 'Retention Rate'}
            )
            retention_intervals_chart = create_chart(writer.book, 'column', 'Retention Rate in Specific Intervals', sheet_name, start_row, col_retention_intervals, len(retention_intervals_df_), value_col = col_retention_intervals+2)
            worksheet.insert_chart(start_row + 18, col_retention_intervals + 5, retention_intervals_chart)

        if feature_feature_engagement_metrics.DropOffPoints:
            drop_off_points_df = pd.DataFrame(feature_feature_engagement_metrics.DropOffPoints)
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