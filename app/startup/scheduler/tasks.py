import asyncio
from app.database.services.analytics.analysis_service import generate_daily_analytics

############################################################

def daily_analytics():
    print("Daily analytics job running")
    results = asyncio.run(generate_daily_analytics())
    print(f"Daily analytics job completed: {results}")
