import io
import pypandoc
import os
from app.common.utils import print_exception

from app.database.services.analytics.common import get_current_analysis_temp_path, get_storage_key_path
from app.domain_types.schemas.analytics import EngagementMetrics
from app.database.services.analytics.reports.report_generator_images import generate_report_images
from app.database.services.analytics.reports.report_generator_markdown import generate_report_markdown
from app.modules.storage.storage_service import StorageService

###############################################################################

async def generate_report_pdf(
        analysis_code: str,
        metrics: EngagementMetrics) -> str | None:
    try:
        report_folder_path = get_current_analysis_temp_path(analysis_code)

        images_generated = generate_report_images(report_folder_path, metrics)
        if not images_generated:
            return None

        markdown_file_path = os.path.join(report_folder_path, f"report_{analysis_code}.md")
        markdown_generated = await generate_report_markdown(markdown_file_path, metrics, report_folder_path)
        if not markdown_generated:
            return None

        pdf_file_path = os.path.join(report_folder_path, f"report_{analysis_code}.pdf")
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
        storage = StorageService()
        file_name = f"analytics_report_{analysis_code}.pdf"
        storage_location = get_storage_key_path(analysis_code)
        await storage.upload_file_as_object(storage_location, pdf_buffer, file_name)
        pdf_buffer.close()
        return True
    except Exception as e:
        print(f"Error converting Markdown to PDF and uploading to S3: {e}")
        return False
