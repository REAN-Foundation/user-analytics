
import os

from app.database.services.analytics.common import get_analytics_template_path
from app.domain_types.schemas.analytics import (
    EngagementMetrics
)

###############################################################################

async def generate_report_markdown(
        markdown_file_path: str,
        metrics: EngagementMetrics) -> bool:

    # Generate the report
    template_path_ = get_analytics_template_path()
    template_path = os.path.join(template_path_, "analytics-report-template.md")
    template_str = ""
    with open(template_path, "r") as file:
        template_str = file.read()

    # Replace the placeholders in the template
    template_str = template_str.replace("{{report_title}}", metrics.title)

    # Save the report
    with open(markdown_file_path, "w") as file:
        file.write(template_str)

    return True

###############################################################################
