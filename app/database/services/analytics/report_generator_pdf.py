
from datetime import datetime
import json
import os
from app.database.services.analytics.common import get_report_folder_path
from app.domain_types.schemas.analytics import UserEngagementMetrics

###############################################################################

async def generate_user_engagement_report_pdf(
        analysis_code: str, user_engagement_metrics: UserEngagementMetrics) -> str:
    try:
        reports_path = get_report_folder_path()
        pdf_file_path = os.path.join(reports_path, f"user_engagement_report_{analysis_code}.pdf")
        # with open(pdf_file_path, "w") as json_file:
        #     json.dump(user_engagement_metrics.model_dump(), json_file)
        return pdf_file_path
    except Exception as e:
        print(e)
        return ""
