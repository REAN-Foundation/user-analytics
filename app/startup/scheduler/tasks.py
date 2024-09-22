import asyncio
import os
import shutil
import time
from app.database.services.analytics.analysis_service import generate_daily_analytics
from app.database.services.analytics.common import get_report_folder_path

############################################################

def daily_analytics():
    print("Daily analytics job running")
    results = asyncio.run(generate_daily_analytics())
    print(f"Daily analytics job completed: {results}")

############################################################

# Remove old files and folders from the reports directory (older than 2 days)

def cleanup_old_files():

    print("Cleanup old files job running")
    days_old = 2
    report_folder_path = get_report_folder_path()

    # Calculate the cutoff time: files older than this will be removed
    cutoff_time = time.time() - days_old * 86400  # 86400 seconds in a day
    # Traverse the directory
    for root, dirs, files in os.walk(report_folder_path, topdown=False):
        # Remove files older than the cutoff time
        for file in files:
            file_path = os.path.join(root, file)
            mtime = os.path.getmtime(file_path)
            if mtime < cutoff_time:
                try:
                    os.remove(file_path)
                    print(f"Removed file: {file_path}")
                except Exception as e:
                    print(f"Error removing file {file_path}: {e}")

        # Remove empty directories older than the cutoff time
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            mtime = os.path.getmtime(dir_path)
            if mtime < cutoff_time:
                try:
                    shutil.rmtree(dir_path)
                    print(f"Removed directory: {dir_path}")
                except Exception as e:
                    print(f"Error removing directory {dir_path}: {e}")

    # Second pass to clean up any empty directories
    for root, dirs, _ in os.walk(report_folder_path, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if not os.listdir(dir_path):  # Check if the directory is empty
                try:
                    os.rmdir(dir_path)
                    print(f"Removed empty directory: {dir_path}")
                except Exception as e:
                    print(f"Error removing empty directory {dir_path}: {e}")

    print("Cleanup old files job completed")
