
from datetime import datetime
import json
import os
from app.common.utils import print_exception
from app.database.services.analytics.common import get_report_folder_temp_path
from app.domain_types.schemas.analytics import EngagementMetrics
from app.modules.storage.provider.awa_s3_storage_service import AwsS3StorageService

###############################################################################

async def generate_report_json(
        analysis_code: str,
        user_engagement_metrics: EngagementMetrics) -> str:
    try:
        storage = AwsS3StorageService()
        json_content = json.dumps(user_engagement_metrics.model_dump(mode='json'), indent=4)
        file_name = f"analytics_report_{analysis_code}.json"
        await storage.upload_object(json_content, file_name)
        return file_name
    except Exception as e:
        print_exception(e)
        return ""
