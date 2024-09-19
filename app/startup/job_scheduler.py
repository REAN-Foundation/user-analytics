from apscheduler.schedulers.background import BackgroundScheduler
import time
from app.database.services.analytics.analysis_service import generate_daily_analytics

###############################################################################

scheduler: BackgroundScheduler = None

# Initialize the APScheduler and start it
def start_scheduler():

    scheduler = BackgroundScheduler()

    # Schedule the task - this runs every day at 1:30 (morning)
    scheduler.add_job(generate_daily_analytics, 'cron', hour=1, minute=30)

    # To run the task every 5 minute (for testing):
    scheduler.add_job(generate_daily_analytics, 'interval', minutes=5)

    scheduler.start()
