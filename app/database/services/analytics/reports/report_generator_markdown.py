
import asyncio
import os
from typing import List

import pandas as pd
from app.database.services.analytics.reports.report_utilities import (
    plot_bar_chart,
    plot_pie_chart,
    reindex_dataframe_to_all_dates
)
from app.domain_types.schemas.analytics import (
    BasicAnalyticsStatistics,
    EngagementMetrics,
    FeatureEngagementMetrics,
    GenericEngagementMetrics
)

###############################################################################

async def generate_report_markdown(
        report_folder_path: str,
        metrics: EngagementMetrics) -> bool:

    pass

###############################################################################
