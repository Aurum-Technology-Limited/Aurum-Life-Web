#!/usr/bin/env python3
"""
Scheduled job runner for Aurum Life
Handles recurring task generation, notifications, and other background tasks
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
from notification_service import notification_service

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
    async def run_notifications_job():
        """Process due notifications and reminders"""
        try:
            print(f"[{datetime.now()}] Processing notifications...")
            
            # Process due reminders
            sent_count = await notification_service.process_due_reminders()
            
            # Check for overdue tasks and create notifications
            overdue_count = await notification_service.check_overdue_tasks()
            
            if sent_count > 0 or overdue_count > 0:
                print(f"[{datetime.now()}] Notifications processed: {sent_count} sent, {overdue_count} overdue tasks found")
            
        except Exception as e:
            print(f"[{datetime.now()}] Error in notifications job: {e}")

    @staticmethod
    async def run_daily_cleanup():
        """Daily cleanup tasks"""
        try:
            print(f"[{datetime.now()}] Running daily cleanup...")
            
            # Clean up old notifications (keep for 30 days)
            from datetime import timedelta
            from database import delete_documents
            
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            # Clean up old browser notifications
            await delete_documents("browser_notifications", {"created_at": {"$lt": cutoff_date}})
            
            # Clean up old sent reminders
            await delete_documents("task_reminders", {
                "is_sent": True,
                "sent_at": {"$lt": cutoff_date}
            })
            
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
    
    # Process notifications every 5 minutes
    schedule.every(5).minutes.do(run_async_job, ScheduledJobs.run_notifications_job)
    
    # Run daily cleanup at 2 AM
    schedule.every().day.at("02:00").do(run_async_job, ScheduledJobs.run_daily_cleanup)
    
    print("Scheduled jobs configured:")
    print("- Recurring tasks: Every hour")
    print("- Notifications: Every 5 minutes")
    print("- Daily cleanup: 2:00 AM daily")

def main():
    """Main job runner loop"""
    print("Starting Aurum Life Scheduled Jobs Runner...")
    setup_schedule()
    
    # Run initial jobs
    print("Running initial recurring tasks generation...")
    run_async_job(ScheduledJobs.run_recurring_tasks_job)
    
    print("Running initial notifications check...")
    run_async_job(ScheduledJobs.run_notifications_job)
    
    print("Job scheduler started. Press Ctrl+C to stop.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(30)  # Check every 30 seconds
    except KeyboardInterrupt:
        print("\nScheduled jobs runner stopped.")

if __name__ == "__main__":
    main()