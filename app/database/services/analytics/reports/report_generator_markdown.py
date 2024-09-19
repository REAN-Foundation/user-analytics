
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
    # template_str = template_str.replace("{{report_title}}", metrics.title)

    image_width = 1300

    report_details_table_str = generate_report_details_table(metrics)
    template_str = template_str.replace("{{report_details_table}}", report_details_table_str)

    basic_statistics_overview_table_str = generate_basic_statistics_overview_table(metrics)
    template_str = template_str.replace("{{basic_statistics_overview_table}}", basic_statistics_overview_table_str)

    registration_history_chart_str = f"""<img src="./registration_history.png" width="{image_width}">"""
    template_str = template_str.replace("{{registration_history_chart}}", registration_history_chart_str)

    deregistration_history_chart_str = f"""<img src="./deregistration_history.png" width="{image_width}">"""
    template_str = template_str.replace("{{deregistration_history_chart}}", deregistration_history_chart_str)

    age_distribution_chart_str = f"""<img src="./age_distribution.png" width="{image_width}">"""
    template_str = template_str.replace("{{age_distribution_chart}}", age_distribution_chart_str)

    age_distribution_table_str = generate_age_distribution_table(metrics)
    template_str = template_str.replace("{{age_distribution_table}}", age_distribution_table_str)

    gender_distribution_chart_str = f"""<img src="./gender_distribution.png" width="{image_width}">"""
    template_str = template_str.replace("{{gender_distribution_chart}}", gender_distribution_chart_str)

    gender_distribution_table_str = generate_gender_distribution_table(metrics)
    template_str = template_str.replace("{{gender_distribution_table}}", gender_distribution_table_str)


    # Save the report
    with open(markdown_file_path, "w") as file:
        file.write(template_str)

    return True

###############################################################################

def generate_report_details_table(metrics: EngagementMetrics) -> str:

    tenant_id = metrics.TenantId if metrics.TenantId is not None else "Unspecified"
    tenant_name = metrics.TenantName if metrics.TenantName is not None else "Unspecified"
    start_date = metrics.StartDate if metrics.StartDate is not None else "Unspecified"
    end_date = metrics.EndDate if metrics.EndDate is not None else "Unspecified"

    return f""" """

def generate_basic_statistics_overview_table(metrics: EngagementMetrics) -> str:

    total_users = metrics.TotalUsers if metrics.TotalUsers is not None else "Unspecified"
    total_active_users = metrics.TotalActiveUsers if metrics.TotalActiveUsers is not None else "Unspecified"
    total_inactive_users = metrics.TotalInactiveUsers if metrics.TotalInactiveUsers is not None else "Unspecified"

    return f""" """

def generate_age_distribution_table(metrics: EngagementMetrics) -> str:

    return f""" """

def generate_gender_distribution_table(metrics: EngagementMetrics) -> str:

    return f""" """

