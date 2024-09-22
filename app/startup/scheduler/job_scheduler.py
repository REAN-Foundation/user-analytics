from apscheduler.schedulers.background import BackgroundScheduler
from app.startup.scheduler.tasks import cleanup_old_files, daily_analytics

###############################################################################

class JobScheduler:

    _scheduler: BackgroundScheduler = BackgroundScheduler()

    @staticmethod
    def start_scheduler():

        try:

            # CRONs
            # Daily Analytics runs every day at 1:30 (morning)
            JobScheduler._scheduler.add_job(daily_analytics, 'cron', hour=1, minute=30)

            # Cleanup old files runs every day at 2:30 (morning)
            JobScheduler._scheduler.add_job(cleanup_old_files, 'cron', hour=2, minute=0)

            # Intervals based tasks
            # To run the task every 5 minute (for testing):
            # JobScheduler._scheduler.add_job(daily_analytics, 'interval', minutes=5)

            # JobScheduler._scheduler.add_job(cleanup_old_files, 'interval', minutes=5)

            JobScheduler._scheduler.start()
            print("Scheduler started successfully")

        except Exception as e:
            print(f"Error starting scheduler: {e}")
