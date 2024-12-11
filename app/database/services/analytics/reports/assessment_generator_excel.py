
import pandas as pd
from app.database.services.analytics.reports.report_utilities import add_title_and_description, write_data_to_excel
from app.domain_types.schemas.analytics import AssessmentEngagementMetrics


async def assessment_engagement(
    assessment_metrics: AssessmentEngagementMetrics,
    writer,
    ) -> bool:
    
    try:      
        start_row = 1
        start_col = 1
        current_row = start_row + 3
        sheet_name = 'Assessment'
        
        if sheet_name not in writer.sheets:
            worksheet = writer.book.add_worksheet(sheet_name)
        else:
            worksheet = writer.sheets[sheet_name]
            
        # title = f"Assessment Engagement Metrics"
        # description = "This section focuses on how users interact with specific features, including access frequency, usage duration, and drop-off points."
        
        # add_title_and_description(
        #     worksheet = worksheet,
        #     title = title,
        #     description = description,
        #     start_row = start_row,
        #     start_col = start_col,
        #     workbook = writer.book,
        # )
        
        if len(assessment_metrics.CareplanWiseAssessmentCompletionCount) > 0:
            columns_to_include = [
                'care_plan_code',
                'completed_assessment_count',
                'in_progress_assessment_count',
            ]
            careplan_assessment_df = pd.DataFrame(assessment_metrics.CareplanWiseAssessmentCompletionCount)[columns_to_include]
            write_data_to_excel(
                data_frame = careplan_assessment_df,
                sheet_name = sheet_name,
                start_row = current_row,
                start_col = start_col,
                writer = writer,
                title = 'Careplan Specific Assessment Metrics',
                rename_columns = {'care_plan_code': 'Careplan code', 'completed_assessment_count': 'Completed Count', 'in_progress_assessment_count': 'In Progress Count'},
                description = 'It shows the count of users who completed or are in progress with assessments, segmented by care plan code.'
            )
            current_row = current_row + len(careplan_assessment_df) + 6
        
        if len(assessment_metrics.CustomAssessmentCompletionCount) > 0:
            columns_to_include = [
                'action_type',
                'completed_assessment_count',
                'in_progress_assessment_count',
            ]
            custom_assessment_df = pd.DataFrame(assessment_metrics.CustomAssessmentCompletionCount)[columns_to_include]
            write_data_to_excel(
                data_frame = custom_assessment_df,
                sheet_name = sheet_name,
                start_row = current_row,
                start_col = start_col,
                writer = writer,
                title = 'Overall Assessment Metrics',
                rename_columns = {'action_type': 'Category', 'completed_assessment_count': 'Completed Count', 'in_progress_assessment_count': 'In Progress Count'},
                description = 'It shows the count of users who completed or are in progress with assessments, segmented by category.'
            )
            current_row = current_row + len(custom_assessment_df) + 6
            
        if len(assessment_metrics.AssessmentQueryResponseDetails) > 0:
            
            title = 'Assessment Query Response Metrics'
            description = 'Analyzes user responses to identify trends and patterns for each assessment question.'
            
            add_title_and_description(
                worksheet = worksheet,
                title = title,
                description = description,
                start_row = current_row,
                start_col = start_col,
                workbook = writer.book,
            )
            current_row = current_row + 6
            assessment_query_response = assessment_metrics.AssessmentQueryResponseDetails
            assessment_titles = set(
                item.get("assessment_template_title", "Unknown")
                for item in assessment_query_response
                if item and "assessment_template_title" in item
            )
            columns_to_include = [
                'node_title',
                'query_response_type',
                'response_option_text',
                'response_count',
            ]
            for title in assessment_titles:
                assessment_data = [item for item in assessment_query_response if item.get("assessment_template_title") == title]
                assessment_query_response_df = pd.DataFrame(assessment_data)[columns_to_include]
                # assessment_query_response_df.rename(
                #     columns={
                #         "node_title": "Question",
                #         "query_response_type": "Response Type",
                #         "response_option_text": "Response Text",
                #         "response_count": "Response Count",
                #     },
                #     inplace=True,
                # )
                write_data_to_excel(
                    data_frame = assessment_query_response_df,
                    sheet_name = sheet_name,
                    start_row = current_row,
                    start_col = start_col,
                    writer = writer,
                    title = f'Assessment Title - {title}',
                    rename_columns = {'node_title': 'Question',
                        'query_response_type': 'Response Type',
                        'response_option_text': 'Response Text',
                        'response_count': 'Response Count'},
                    description = ''
                )
                current_row = current_row + len(assessment_query_response_df) + 6
    
                    
    except Exception as e:
        print(f"Error generating assessment engagement excel report: {e}")
        return ""