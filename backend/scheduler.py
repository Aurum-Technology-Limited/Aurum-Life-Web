#!/usr/bin/env python3
"""
Scheduled job runner for Aurum Life
Handles recurring task generation and other background tasks
"""

import asyncio
import schedule
import time
from datetime import datetime
import os
import sys

# Add the backend directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services import RecurringTaskService

class ScheduledJobs:
    @staticmethod
    async def run_recurring_tasks_job():
        """Generate recurring task instances"""
        try:
            print(f"[{datetime.now()}] Running recurring tasks job...")
            await RecurringTaskService.generate_recurring_task_instances()
            print(f"[{datetime.now()}] Recurring tasks job completed")
        except Exception as e:
            print(f"[{datetime.now()}] Error in recurring tasks job: {e}")

    @staticmethod
    async def run_daily_cleanup():
        """Daily cleanup tasks"""
        try:
            print(f"[{datetime.now()}] Running daily cleanup...")
            # Add cleanup logic here (e.g., remove old completed tasks, archive old data)
            print(f"[{datetime.now()}] Daily cleanup completed")
        except Exception as e:
            print(f"[{datetime.now()}] Error in daily cleanup: {e}")

def run_async_job(job_func):
    """Wrapper to run async jobs with schedule"""
    asyncio.run(job_func())

def setup_schedule():
    """Set up the job schedule"""
    # Generate recurring task instances every hour
    schedule.every().hour.do(run_async_job, ScheduledJobs.run_recurring_tasks_job)
    
    # Run daily cleanup at 2 AM
    schedule.every().day.at("02:00").do(run_async_job, ScheduledJobs.run_daily_cleanup)
    
    print("Scheduled jobs configured:")
    print("- Recurring tasks: Every hour")
    print("- Daily cleanup: 2:00 AM daily")

def main():
    """Main job runner loop"""
    print("Starting Aurum Life Scheduled Jobs Runner...")
    setup_schedule()
    
    # Run initial recurring tasks generation
    print("Running initial recurring tasks generation...")
    run_async_job(ScheduledJobs.run_recurring_tasks_job)
    
    print("Job scheduler started. Press Ctrl+C to stop.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\nScheduled jobs runner stopped.")

if __name__ == "__main__":
    main()