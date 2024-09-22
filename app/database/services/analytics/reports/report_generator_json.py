
from datetime import datetime
import json
import os
from app.common.utils import print_exception
from app.database.services.analytics.common import get_storage_key_path
from app.domain_types.schemas.analytics import EngagementMetrics
from app.modules.storage.storage_service import StorageService

###############################################################################

async def generate_report_json(
        analysis_code: str,
        user_engagement_metrics: EngagementMetrics) -> str:
    try:
        storage = StorageService()
        json_content = json.dumps(user_engagement_metrics.model_dump(mode='json'), indent=4)
        file_name = f"analytics_report_{analysis_code}.json"
        storage_location = get_storage_key_path(analysis_code)
        await storage.upload_file_as_object(storage_location, json_content, file_name)
        return file_name
    except Exception as e:
        print_exception(e)
        return ""
