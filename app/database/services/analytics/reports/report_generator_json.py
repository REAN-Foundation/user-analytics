
from datetime import datetime
import json
import os
from app.database.services.analytics.common import get_report_folder_path
from app.domain_types.schemas.analytics import GenericEngagementMetrics
from app.modules.storage.provider.awa_s3_storage_service import S3Storage

###############################################################################
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
region_name = os.getenv('AWS_REGION')
bucket_name = os.getenv('AWS_BUCKET')
###############################################################################

# async def generate_user_engagement_report_json(
#         analysis_code: str, user_engagement_metrics: GenericEngagementMetrics) -> str:
#     try:
#         reports_path = get_report_folder_path()
#         json_file_path = os.path.join(reports_path, f"user_engagement_report_{analysis_code}.json")
#         with open(json_file_path, "w") as json_file:
#             json.dump(user_engagement_metrics.model_dump(mode='json'), json_file, indent=4)
#         return json_file_path
#     except Exception as e:
#         print(e)
#         return ""

async def generate_report_json(
        analysis_code: str, user_engagement_metrics: GenericEngagementMetrics) -> str:
    try:
        storage = S3Storage(aws_access_key_id, aws_secret_access_key, region_name)
        json_content = json.dumps(user_engagement_metrics.model_dump(mode='json'), indent=4)
        file_name = f"user_engagement_report_{analysis_code}.json"
        await storage.upload_object(json_content, bucket_name, file_name)
        s3_file_url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
        return s3_file_url
    except Exception as e:
        print(e)
        return ""
