import pandas as pd
from app.database.services.analytics.reports.report_utilities import(
  add_title_and_description,
  create_chart,
  reindex_dataframe_to_all_missing_dates,
  write_data_to_excel
  )
from app.domain_types.schemas.analytics import FeatureEngagementMetrics

####################################################################################

async def feature_engagement(feature_feature_engagement_metrics: FeatureEngagementMetrics, writer, sheet_name:str):
    try:      
        start_row = 1
        start_col = 1
        graph_pos = 7
        current_row = start_row + 6

        sheet_name = format_sheet_name(sheet_name)
        
        if sheet_name not in writer.sheets:
            worksheet = writer.book.add_worksheet(sheet_name)
        else:
            worksheet = writer.sheets[sheet_name]
            
        title = f"{sheet_name} Engagement Metrics"
        description = "This section focuses on how users interact with specific features, including access frequency, usage duration, and drop-off points."
        
        add_title_and_description(
            worksheet = worksheet,
            title = title,
            description = description,
            start_row = start_row,
            start_col = start_col,
            workbook = writer.book,
        )
            
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
                start_row = current_row,
                start_col = start_col,
                writer = writer,
                title = 'Access Frequency',
                rename_columns = {'month': 'Month', 'access_frequency': 'Access Frequency'},
                description = 'The number of times users access a particular feature over time. This metric helps identify the popularity and utility of features among users.'
            )
            access_frequency_chart = create_chart(
                workbook = writer.book, 
                chart_type = 'column', 
                series_name = 'Access Frequency', 
                sheet_name = sheet_name, 
                start_row = current_row + 2,
                start_col = start_col, 
                df_len = len(access_frequency_df_), 
                value_col = start_col + 1)
            worksheet.insert_chart(current_row + 2, graph_pos, access_frequency_chart)
            current_row = current_row + len(access_frequency_df_) + 6
            
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
                    start_row = current_row,
                    start_col = start_col,
                    writer = writer,
                    title = 'Engagement Rate',
                    rename_columns = {'month': 'Month','feature':'Feature', 'engagement_rate': 'Engagement Rate'},
                    description = 'This is the ratio of number of unique users engaging with each feature per month to the total number of active users per month.'
                )     
                engagement_rate_chart = create_chart(
                    workbook = writer.book,
                    chart_type = 'column',
                    series_name = 'Engagement Rate',
                    sheet_name = sheet_name,
                    start_row = current_row + 2,
                    start_col = start_col,
                    df_len = len(engagement_rate_df),
                    value_col = start_col + 2
                )
                worksheet.insert_chart(current_row + 2, graph_pos, engagement_rate_chart)
                current_row = current_row + len(engagement_rate_df) + 6

        if feature_feature_engagement_metrics.RetentionRateOnSpecificDays:
            retention_specific_days = feature_feature_engagement_metrics.RetentionRateOnSpecificDays['retention_on_specific_days']
            retention_days_df= pd.DataFrame(retention_specific_days)
            retention_days_df_ = write_data_to_excel(
                data_frame = retention_days_df,
                sheet_name = sheet_name,
                start_row = current_row,
                start_col = start_col,
                writer = writer,
                title = 'Retention Rate on Specific Days',
                rename_columns = {'day': 'Day', 'returning_users': 'Returning Users', 'retention_rate': 'Retention Rate'},
                description = 'The percentage of users who return to a feature after their first use at specific intervals (day 1, day 7, day 30). Retention rates measure user loyalty and the ability of the feature to keep users engaged over time.'
            )
            retention_days_chart = create_chart(
                workbook = writer.book,
                chart_type = 'column',
                series_name = 'Retention Rate on Specific Days', 
                sheet_name = sheet_name,
                start_row = current_row + 2,
                start_col = start_col,
                df_len = len(retention_days_df_),
                value_col = start_col + 2
            )
            worksheet.insert_chart(current_row + 2, graph_pos, retention_days_chart)
            current_row = current_row + len(retention_days_df_) + 12

        if feature_feature_engagement_metrics.RetentionRateInSpecificIntervals:
            retention_intervals = feature_feature_engagement_metrics.RetentionRateInSpecificIntervals['retention_in_specific_interval']
            retention_intervals_df = pd.DataFrame(retention_intervals)

            retention_intervals_df_ = write_data_to_excel(
                data_frame = retention_intervals_df,
                sheet_name = sheet_name,
                start_row = current_row,
                start_col = start_col,
                writer = writer,
                title = 'Retention Rate in Specific Intervals',
                rename_columns = {'interval': 'Interval', 'returning_users': 'Returning Users', 'retention_rate': 'Retention Rate'},
                description = 'The percentage of users who return to a feature after their first use at specific intervals (0-1 days, 1-3 days, 3-7 days, etc). This is just another way to look at the retention on specific days.'
            )
            retention_intervals_chart = create_chart(
            workbook = writer.book,
                chart_type = 'column',
                series_name = 'Retention Rate in Specific Intervals',
                sheet_name = sheet_name,
                start_row = current_row + 2,
                start_col = start_col,
                df_len = len(retention_intervals_df_),
                value_col = start_col + 2
            )
            worksheet.insert_chart(current_row + 2, graph_pos, retention_intervals_chart)
            current_row = current_row + len(retention_intervals_df_) + 12

        if feature_feature_engagement_metrics.DropOffPoints:
            drop_off_points_df = pd.DataFrame(feature_feature_engagement_metrics.DropOffPoints)
            drop_off_points_df['dropoff_rate'] = pd.to_numeric(drop_off_points_df['dropoff_rate'], errors='coerce')
            drop_off_points_df['dropoff_count'] = pd.to_numeric(drop_off_points_df['dropoff_count'], errors='coerce')
            drop_off_points_df_ = write_data_to_excel(
                data_frame = drop_off_points_df,
                sheet_name = sheet_name,
                start_row = current_row,
                start_col = start_col,
                writer = writer,
                title = 'Dropoff Points',
                rename_columns = {'event_name': 'Event Name', 'dropoff_count':'Dropoff Count','total_users':'Total Users', 'dropoff_rate': 'Dropoff Rate'},
                description = 'Points in the user flow where users most frequently stop using a feature. Identifying drop-off points helps in optimizing the user journey and addressing usability challenges to improve feature completion rates.These are found by identifying the most common sequences of events that lead to users dropping off from a feature.'
            )  
            # drop_off_points_chart = create_chart(
            #     workbook = writer.book,
            #     chart_type = 'pie',
            #     series_name = 'Dropoff Points',
            #     sheet_name = sheet_name,
            #     start_row = current_row + 2,
            #     start_col = start_col,
            #     df_len = len(drop_off_points_df_),
            #     value_col = start_col + 1
            # )
            # worksheet.insert_chart(current_row + 2, graph_pos, drop_off_points_chart)
    except Exception as e:
        print(f"Error generating report: {e}")
        return ""
    
  ##################################################################################
      
def format_sheet_name(feature_name):
    formatted_name = feature_name.replace('-', ' ').title()
    return formatted_name  