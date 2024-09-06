
from datetime import datetime
import json
import os
from app.database.services.analytics.common import get_report_folder_path
from app.domain_types.schemas.analytics import UserEngagementMetrics
import pandas as pd

###############################################################################

async def generate_user_engagement_report_excel(
        analysis_code: str, user_engagement_metrics: UserEngagementMetrics) -> str:
    try:
        reports_path = get_report_folder_path()
        excel_file_path = os.path.join(reports_path, f"user_engagement_report_{analysis_code}.xlsx")
        with pd.ExcelWriter(excel_file_path) as writer:
            await add_daily_active_users(user_engagement_metrics.DailyActiveUsers, writer)
            await add_weekly_active_users(user_engagement_metrics.WeeklyActiveUsers, writer)
        return excel_file_path
    except Exception as e:
        print(e)
        return ""

###############################################################################

async def add_daily_active_users(daily_active_users: list|None, writer) -> None:
    try:
        if daily_active_users:
            df = pd.DataFrame(daily_active_users)
            df.to_excel(writer, sheet_name='Daily Active Users', index=False)
            # Access the xlsxwriter workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets["Daily Active Users"]
            worksheet.conditional_format(1, 2, len(df), 2,
                             {'type': '3_color_scale'})
            # Create a chart object (Line chart for example)
            chart = workbook.add_chart({'type': 'column'})

            # Define the range for the chart data
            # First column -> Date
            # Second column -> Daily Active Users
            chart.add_series({
                'name': 'Daily Active Users',
                'categories': ['Daily Active Users', 1, 0, len(df), 0],  # Date range
                'values': ['Daily Active Users', 1, 1, len(df), 1],      # Active users range
            })

            # Add chart title and labels
            chart.set_title({'name': 'Daily Active Users Over Time'})
            chart.set_x_axis({'name': 'Date'})
            chart.set_y_axis({'name': 'Active Users'})

            # Insert the chart into the worksheet
            worksheet.insert_chart('E2', chart)

    except Exception as e:
        print(e)

async def add_weekly_active_users(weekly_active_users: list|None, writer) -> None:
    try:
        if weekly_active_users:
            df = pd.DataFrame(weekly_active_users)
            df.to_excel(writer, sheet_name='Weekly Active Users', index=False)
            # Access the xlsxwriter workbook and worksheet objects
            workbook = writer.book
            worksheet = writer.sheets["Weekly Active Users"]
            worksheet.conditional_format(1, 2, len(df), 2,
                             {'type': '3_color_scale'})
            # Create a chart object (Line chart for example)
            chart = workbook.add_chart({'type': 'column'})

            # Define the range for the chart data
            # First column -> Date
            # Second column -> Weekly Active Users
            chart.add_series({
                'name': 'Weekly Active Users',
                'categories': ['Weekly Active Users', 1, 0, len(df), 0],  # Date range
                'values': ['Weekly Active Users', 1, 1, len(df), 1],      # Active users range
            })

            # Add chart title and labels
            chart.set_title({'name': 'Weekly Active Users Over Time'})
            chart.set_x_axis({'name': 'Date'})
            chart.set_y_axis({'name': 'Active Users'})

            # Insert the chart into the worksheet
            worksheet.insert_chart('E2', chart)

    except Exception as e:
        print(e)

