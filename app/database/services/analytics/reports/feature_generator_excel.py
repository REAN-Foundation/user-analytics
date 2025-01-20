import json
import pandas as pd
from app.database.services.analytics.reports.report_utilities import(
  add_title_and_description,
  create_chart,
  reindex_dataframe_to_all_missing_dates,
  write_data_to_excel
  )
from app.domain_types.schemas.analytics import FeatureEngagementMetrics, HealthJourneyEngagementMetrics, PatientTaskEngagementMetrics

####################################################################################

async def feature_engagement(
    feature_engagement_metrics: FeatureEngagementMetrics,
    writer, sheet_name:str,
    medication_management_metrics:list | None,
    health_journey_metrics:HealthJourneyEngagementMetrics,
    patient_task_metrics:PatientTaskEngagementMetrics,
    vitals_task_metrics:list | None
    ) -> bool:
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
            
        if len(feature_engagement_metrics.AccessFrequency) > 0:
            access_frequency_df = pd.DataFrame(feature_engagement_metrics.AccessFrequency) 
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
            current_row = current_row + len(access_frequency_df_) + 12
                
        if len(feature_engagement_metrics.EngagementRate) > 0:
                engagement_rate_df= pd.DataFrame(feature_engagement_metrics.EngagementRate)
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
                if not engagement_rate_df.empty:
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
                    current_row = current_row + len(engagement_rate_df) + 12

        if len(feature_engagement_metrics.RetentionRateOnSpecificDays) > 0:
            retention_specific_days = feature_engagement_metrics.RetentionRateOnSpecificDays['retention_on_specific_days']
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
            if not retention_days_df.empty:
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

        if len(feature_engagement_metrics.RetentionRateInSpecificIntervals) > 0:
            retention_intervals = feature_engagement_metrics.RetentionRateInSpecificIntervals['retention_in_specific_interval']
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
            if not retention_intervals_df.empty:
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

        if feature_engagement_metrics.DropOffPoints:
            drop_off_points_df = pd.DataFrame(feature_engagement_metrics.DropOffPoints)
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
            current_row += len(drop_off_points_df) + 6
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
         
        if feature_engagement_metrics.Feature == 'medication' and medication_management_metrics:
            medication_data = medication_management_metrics[0]
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

            medication_df_ = write_data_to_excel(
                data_frame=medication_df,
                sheet_name=sheet_name,
                start_row=current_row,
                start_col=start_col,
                writer=writer,
                title='Medication Managemnent',
                description='The medication adherence showing the percentage of scheduled doses taken on time, alongside the number and percentage of missed doses.'
            )

            if not medication_df.empty:
                medication_chart = create_chart(
                    workbook=writer.book,
                    chart_type='pie',
                    series_name='Medication Managemnent',
                    sheet_name=sheet_name,
                    start_row=current_row + 2,
                    start_col=start_col,
                    df_len=len(medication_df_),
                    value_col=start_col + 1
                )
                worksheet.insert_chart(current_row + 2, graph_pos, medication_chart)
            
        if feature_engagement_metrics.Feature == 'careplan' and health_journey_metrics:
            overall_health_journey_data = health_journey_metrics.Overall
            overall_completed_tasks = overall_health_journey_data['health_journey_completed_task_count']
            overall_not_completed_tasks = overall_health_journey_data['health_journey_task_count'] - overall_completed_tasks
            health_journey_labels = ['Completed', 'Not Completed']
            overall_health_journey_values = [
                overall_completed_tasks,
                overall_not_completed_tasks
            ]

            overall_task_df = pd.DataFrame({
                'Status': health_journey_labels,
                'Count': overall_health_journey_values
            })
            
            overall_task_df = write_data_to_excel(
                data_frame=overall_task_df,
                sheet_name=sheet_name,
                start_row=current_row,
                start_col=start_col,
                writer=writer,
                title=f'Overall health journey task metrics',
                description='The health journey tasks showing the number of completed and not completed tasks for the care plan.'
            )

            if not overall_task_df.empty:
                overall_health_journey_chart = create_chart(
                    workbook=writer.book,
                    chart_type='pie',
                    series_name=f'Overall health journey task metrics',
                    sheet_name=sheet_name,
                    start_row=current_row + 2,
                    start_col=start_col,
                    df_len=len(overall_task_df),
                    value_col=start_col + 1
                )

                worksheet.insert_chart(current_row + 2, graph_pos, overall_health_journey_chart)
                current_row += len(overall_task_df) + 18
    
            health_journey_tasks_data, unique_careplan_codes = health_journey_tasks(health_journey_metrics)
            for plan_code in unique_careplan_codes:
                specific_careplan_data = [task for task in health_journey_tasks_data if task['PlanCode'] == plan_code]
                
                if specific_careplan_data:
                    completed_count = specific_careplan_data[0].get('careplan_completed_task_count', 0)
                    not_completed_count = specific_careplan_data[0].get('careplan_not_completed_task_count', 0)

                    health_journey_df = pd.DataFrame({
                        'Status': health_journey_labels,
                        'Count': [completed_count, not_completed_count]
                    })

                    health_journey_df_ = write_data_to_excel(
                        data_frame=health_journey_df,
                        sheet_name=sheet_name,
                        start_row=current_row,
                        start_col=start_col,
                        writer=writer,
                        title=f'Health journey task metrics for {plan_code}',
                        description='The health journey tasks showing the number of completed and not completed tasks for the care plan.'
                    )

                    if not health_journey_df_.empty:
                        health_journey_chart = create_chart(
                            workbook=writer.book,
                            chart_type='pie',
                            series_name=f'Health journey task metrics for {plan_code}',
                            sheet_name=sheet_name,
                            start_row=current_row + 2,
                            start_col=start_col,
                            df_len=len(health_journey_df_),
                            value_col=start_col + 1
                        )

                        worksheet.insert_chart(current_row + 2, graph_pos, health_journey_chart)
                
                current_row += len(health_journey_df) + 18
                
        if feature_engagement_metrics.Feature == 'user-task' and patient_task_metrics:
            overall_patient_task_metrics = patient_task_metrics.Overall
            category_specific_data = patient_task_metrics.CategorySpecific
            overall_completed_tasks = overall_patient_task_metrics['patient_completed_task_count']
            overall_not_completed_tasks = overall_patient_task_metrics['patient_task_count'] - overall_completed_tasks
            patient_task_metrics_labels = ['Completed', 'Not Completed']
            overall_patient_task_metrics_values = [
                overall_completed_tasks,
                overall_not_completed_tasks
            ]

            overall_task_df = pd.DataFrame({
                'Status': patient_task_metrics_labels,
                'Count': overall_patient_task_metrics_values
            })
            
            overall_task_df = write_data_to_excel(
                data_frame=overall_task_df,
                sheet_name=sheet_name,
                start_row=current_row,
                start_col=start_col,
                writer=writer,
                title=f'Overall patient task metrics',
                description='The patient tasks metrics showing the number of completed and not completed tasks.'
            )

            if not overall_task_df.empty:
                overall_health_journey_chart = create_chart(
                    workbook=writer.book,
                    chart_type='pie',
                    series_name=f'Overall patient task metrics',
                    sheet_name=sheet_name,
                    start_row=current_row + 2,
                    start_col=start_col,
                    df_len=len(overall_task_df),
                    value_col=start_col + 1
                )

                worksheet.insert_chart(current_row + 2, graph_pos, overall_health_journey_chart)
                current_row += len(overall_task_df) + 18
            
            for category in category_specific_data:
                task_category = category['task_category']
                completed = category.get('patient_completed_task_count', 0)
                total_tasks = category.get('task_count', 0)
                not_completed = total_tasks - completed

                category_task_df = pd.DataFrame({
                    "Status": ["Completed", "Not Completed"],
                    "Count": [completed, not_completed]
                })

                category_task_df = write_data_to_excel(
                    data_frame = category_task_df,
                    sheet_name = sheet_name,
                    start_row = current_row,
                    start_col = start_col,
                    writer = writer,
                    title = f'{task_category} task metrics',
                    description = f'The patient tasks metrics showing the number of completed and not completed tasks for {task_category}.'
                )

                if not category_task_df.empty:
                    category_pie_chart = create_chart(
                        workbook = writer.book,
                        chart_type = 'pie',
                        series_name = f'{task_category} task metrics',
                        sheet_name = sheet_name,
                        start_row = current_row + 2, 
                        start_col = start_col,
                        df_len = len(category_task_df),
                        value_col = start_col + 1
                    )

                    worksheet.insert_chart(current_row + 2, graph_pos, category_pie_chart)

                
                    current_row += len(category_task_df) + 18 
                    
            if len(feature_engagement_metrics.Feature == 'user-task' and patient_task_metrics.QuarterWiseTaskCompletionMetrics):
                quarterwise_task_completion_df = pd.DataFrame(patient_task_metrics.QuarterWiseTaskCompletionMetrics)
                write_data_to_excel(
                    data_frame = quarterwise_task_completion_df,
                    sheet_name = sheet_name,
                    start_row = current_row,
                    start_col = start_col,
                    writer = writer,
                    title = 'Quarterwise Task Completion Metrics',
                    rename_columns = {'percentage_range': 'Percentage Range', 'user_count': 'User Count'},
                    description = 'This shows the count of users grouped by task completion percentage ranges.'
                )
                    
        if feature_engagement_metrics.Feature == 'vitals' and vitals_task_metrics:
            # vitals_task_data = vitals_task_metrics[0]
            for vital_task in vitals_task_metrics:
                vital_name_ = vital_task['vital_name'].value
                vital_name = vital_name_.replace('-', ' ').title()
                manual_entry_count = vital_task.get('manual_entry_add_event_count', 0)
                device_entry_count = vital_task.get('device_entry_add_event_count', 0)
                vital_task_df = pd.DataFrame({
                    "Status": ["Manual Entry Count", "Device Entry Count"],
                    "Count": [manual_entry_count, device_entry_count]
                })
                
                vital_task_df = write_data_to_excel(
                    data_frame = vital_task_df,
                    sheet_name = sheet_name,
                    start_row = current_row,
                    start_col = start_col,
                    writer = writer,
                    title = f'{vital_name} task metrics',
                    description = f'This shows the addition rate of vital metrics, comparing the total events logged for each vital metric and their breakdown into manual entries and device-based entries.'
                )

                if not vital_task_df.empty:
                    vital_pie_chart = create_chart(
                        workbook = writer.book,
                        chart_type = 'pie',
                        series_name = f'{vital_name} task metrics',
                        sheet_name = sheet_name,
                        start_row = current_row + 2, 
                        start_col = start_col,
                        df_len = len(vital_task_df),
                        value_col = start_col + 1
                    )

                    worksheet.insert_chart(current_row + 2, graph_pos, vital_pie_chart)

                    current_row += len(vital_task_df) + 18 
                    
    except Exception as e:
        print(f"Error generating feature engagement excel report: {e}")
        return ""
    
  ##################################################################################
      
def format_sheet_name(feature_name):
    formatted_name = feature_name.replace('-', ' ').title()
    return formatted_name  

def health_journey_tasks(health_journey_metrics: HealthJourneyEngagementMetrics):
    health_journey_tasks_data = health_journey_metrics.CareplanSpecific.HealthJourneyWiseTask
    health_journey_completed_task = health_journey_metrics.CareplanSpecific.HealthJourneyWiseCompletedTask
    for task in health_journey_tasks_data:
        completed_task = next(
            (completed for completed in health_journey_completed_task if completed['careplan_code'] == task['PlanCode']),
            None
        )
        
        completed_count = completed_task['careplan_completed_task_count'] if completed_task else 0
        total_task_count = task['careplan_task_count']
        not_completed_count = total_task_count - completed_count
  
        task['careplan_completed_task_count'] = completed_count
        task['careplan_not_completed_task_count'] = not_completed_count
        
        unique_careplan_codes = list(set(
        [task['PlanCode'] for task in health_journey_tasks_data] + 
        [completed['careplan_code'] for completed in health_journey_completed_task]
    ))

    return health_journey_tasks_data, unique_careplan_codes

