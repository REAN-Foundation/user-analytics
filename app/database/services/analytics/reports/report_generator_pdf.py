from asyncio import subprocess
from datetime import datetime
import io
import pypandoc
import json
import os
from app.common.utils import print_exception
from app.database.services.analytics.common import get_report_folder_path
from app.domain_types.schemas.analytics import EngagementMetrics
from app.database.services.analytics.reports.report_generator_images import generate_report_images
from app.database.services.analytics.reports.report_generator_markdown import generate_report_markdown
from app.modules.storage.provider.awa_s3_storage_service import S3Storage

aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
region_name = os.getenv('AWS_REGION')
bucket_name = os.getenv('AWS_BUCKET')
###############################################################################

async def generate_report_pdf(
        analysis_code: str,
        metrics: EngagementMetrics) -> str | None:
    try:
        reports_path = get_report_folder_path()
        report_folder_path = os.path.join(reports_path, f"report_{analysis_code}")
        pdf_file_path = os.path.join(report_folder_path, f"report_{analysis_code}.pdf")
        if not os.path.exists(report_folder_path):
            os.makedirs(report_folder_path, exist_ok=True)

        images_generated = generate_report_images(report_folder_path, metrics)
        if not images_generated:
            return None

        markdown_file_path = os.path.join(report_folder_path, f"report_{analysis_code}.md")
        markdown_generated = await generate_report_markdown(markdown_file_path, metrics)
        if not markdown_generated:
            return None

        pdf_generated = await markdown_to_pdf(markdown_file_path, pdf_file_path, analysis_code)
        if not pdf_generated:
            return None

        return pdf_file_path

    except Exception as e:
        print_exception(e)
        return None

# async def markdown_to_pdf(markdown_file_path: str, pdf_file_path: str) -> bool:
#     try:
#         # Convert Markdown to PDF using Pandoc
#         # subprocess.run(['pandoc', markdown_file_path, '-o', pdf_file_path], check=True)

#         # Ensure the images are in the same directory as the markdown file
#         md_dir = os.path.dirname(markdown_file_path)

#         # Convert markdown to PDF using pandoc
#         output = pypandoc.convert_file(
#             markdown_file_path,
#             'pdf',
#             outputfile=pdf_file_path,
#             extra_args=['--pdf-engine=xelatex'])

#         assert output == "", "There was an issue with the conversion"
#         print(f"PDF generated at {pdf_file_path}")

#         return True
#     except Exception as e:
#         print(f"Error converting Markdown to PDF: {e}")
#         return False

async def markdown_to_pdf(markdown_file_path: str, pdf_file_path: str, analysis_code) -> bool:
    try:
        md_dir = os.path.dirname(markdown_file_path)
        pdf_buffer = io.BytesIO()
        pypandoc.convert_file(
            markdown_file_path,
            'pdf',
            outputfile=pdf_buffer,  # Writing output directly to the buffer
            extra_args=['--pdf-engine=xelatex']
        )
        pdf_buffer.seek(0)
        # analysis_code = '28'
        storage = S3Storage(aws_access_key_id, aws_secret_access_key, region_name)
        file_name = f"user_engagement_report_{analysis_code}.pdf"
        await storage.upload_excel_or_pdf(pdf_buffer, bucket_name, file_name)
        s3_file_url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
        pdf_buffer.close()

        print(f"PDF uploaded to S3 at {s3_file_url}")
        return True
    except Exception as e:
        print(f"Error converting Markdown to PDF and uploading to S3: {e}")
        return False
