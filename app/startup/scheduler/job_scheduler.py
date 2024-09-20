from apscheduler.schedulers.background import BackgroundScheduler
from app.database.services.analytics.analysis_service import generate_daily_analytics
from app.startup.scheduler.tasks import daily_analytics

###############################################################################

class JobScheduler:

    _scheduler: BackgroundScheduler = BackgroundScheduler()

    @staticmethod
    def start_scheduler():

        try:
            # Schedule the task - this runs every day at 1:30 (morning)
            JobScheduler._scheduler.add_job(daily_analytics, 'cron', hour=15, minute=8)

            # To run the task every 5 minute (for testing):
            # JobScheduler._scheduler.add_job(daily_analytics, 'interval', minutes=2)

            JobScheduler._scheduler.start()
            print("Scheduler started successfully")

        except Exception as e:
            print(f"Error starting scheduler: {e}")

