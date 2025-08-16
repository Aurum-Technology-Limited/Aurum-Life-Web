"""
Task Reminders & Notifications Service for Aurum Life
Handles all notification logic including scheduling, sending, and preferences
"""

import os
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, time
from supabase_client import find_document, find_documents, create_document, update_document, delete_document, bulk_update_documents, bulk_delete_documents
from email_service import email_service
from models import (
    NotificationPreference, NotificationPreferenceCreate, NotificationPreferenceUpdate,
    TaskReminder, TaskReminderCreate, NotificationResponse,
    NotificationTypeEnum, NotificationChannelEnum, PriorityEnum,
    Task, Project, User, BrowserNotification
)

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for managing task reminders and notifications"""
    
    @staticmethod
    async def get_user_notification_preferences(user_id: str) -> Optional[NotificationPreference]:
        """Get user's notification preferences"""
        pref_doc = await find_document("notification_preferences", {"user_id": user_id})
        if pref_doc:
            return NotificationPreference(**pref_doc)
        return None
    
    @staticmethod
    async def create_default_notification_preferences(user_id: str) -> NotificationPreference:
        """Create default notification preferences for a new user"""
        default_prefs = NotificationPreferenceCreate()
        pref_data = {
            "user_id": user_id,
            **default_prefs.dict(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await create_document("notification_preferences", pref_data)
        return NotificationPreference(**pref_data)
    
    @staticmethod
    async def update_notification_preferences(user_id: str, updates: NotificationPreferenceUpdate) -> Optional[NotificationPreference]:
        """Update user's notification preferences"""
        # First, find the existing preferences document
        pref_doc = await find_document("notification_preferences", {"user_id": user_id})
        if not pref_doc:
            # Create default preferences if none exist
            return await NotificationService.create_default_notification_preferences(user_id)
        
        update_data = {k: v for k, v in updates.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        success = await update_document(
            "notification_preferences",
            {"id": pref_doc["id"]},  # Use the document ID for Supabase
            update_data
        )
        
        if success:
            return await NotificationService.get_user_notification_preferences(user_id)
        return None
    
    @staticmethod
    async def schedule_task_reminder(user_id: str, task_id: str, notification_type: NotificationTypeEnum, 
                                   scheduled_time: datetime, title: str, message: str,
                                   channels: List[NotificationChannelEnum] = None) -> str:
        """Schedule a task reminder"""
        if channels is None:
            channels = [NotificationChannelEnum.browser]
        
        # Get task details for metadata
        task_doc = await find_document("tasks", {"id": task_id, "user_id": user_id})
        project_name = None
        
        if task_doc:
            task = Task(**task_doc)
            project_doc = await find_document("projects", {"id": task.project_id, "user_id": user_id})
            if project_doc:
                project_name = project_doc["name"]
        
        reminder_data = {
            "id": f"reminder_{task_id}_{int(scheduled_time.timestamp())}",
            "user_id": user_id,
            "task_id": task_id,
            "notification_type": notification_type,
            "scheduled_time": scheduled_time,
            "title": title,
            "message": message,
            "channels": channels,
            "task_name": task_doc.get("name") if task_doc else None,
            "project_name": project_name,
            "priority": task_doc.get("priority") if task_doc else None,
            "is_sent": False,
            "retry_count": 0,
            "max_retries": 3,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await create_document("task_reminders", reminder_data)
        logger.info(f"Scheduled {notification_type} reminder for task {task_id} at {scheduled_time}")
        return reminder_data["id"]
    
    @staticmethod
    async def process_due_reminders() -> int:
        """Process all reminders that are due to be sent"""
        now = datetime.utcnow()
        
        # Find all unsent reminders that are due
        due_reminders = await find_documents("task_reminders", {
            "is_sent": False,
            "scheduled_time": {"$lte": now}
        })
        
        sent_count = 0
        
        for reminder_doc in due_reminders:
            try:
                reminder = TaskReminder(**reminder_doc)
                
                # Check if user preferences allow this notification
                prefs = await NotificationService.get_user_notification_preferences(reminder.user_id)
                if not prefs or not NotificationService._should_send_notification(reminder, prefs, now):
                    continue
                
                # Send the notification
                success = await NotificationService._send_notification(reminder)
                
                if success:
                    # Mark as sent
                    await update_document("task_reminders", 
                                        {"id": reminder.id}, 
                                        {"is_sent": True, "sent_at": now})
                    sent_count += 1
                    logger.info(f"Sent notification: {reminder.title}")
                else:
                    # Handle retry logic
                    await NotificationService._handle_failed_notification(reminder)
                    
            except Exception as e:
                logger.error(f"Error processing reminder {reminder_doc.get('id')}: {e}")
        
        if sent_count > 0:
            logger.info(f"Processed {sent_count} notifications")
        
        return sent_count
    
    @staticmethod
    def _should_send_notification(reminder: TaskReminder, prefs: NotificationPreference, current_time: datetime) -> bool:
        """Check if notification should be sent based on user preferences"""
        
        # Check if notification type is enabled
        type_enabled_map = {
            NotificationTypeEnum.task_due: prefs.task_due_notifications,
            NotificationTypeEnum.task_overdue: prefs.task_overdue_notifications,
            NotificationTypeEnum.task_reminder: prefs.task_reminder_notifications,
            NotificationTypeEnum.project_deadline: prefs.project_deadline_notifications,
            NotificationTypeEnum.recurring_task: prefs.recurring_task_notifications,
        }
        
        if not type_enabled_map.get(reminder.notification_type, True):
            return False
        
        # Check quiet hours
        if prefs.quiet_hours_start and prefs.quiet_hours_end:
            current_time_str = current_time.strftime("%H:%M")
            if prefs.quiet_hours_start <= current_time_str or current_time_str <= prefs.quiet_hours_end:
                logger.debug(f"Skipping notification during quiet hours: {current_time_str}")
                return False
        
        # Check if channels are enabled
        if NotificationChannelEnum.browser in reminder.channels and not prefs.browser_notifications:
            reminder.channels.remove(NotificationChannelEnum.browser)
        
        if NotificationChannelEnum.email in reminder.channels and not prefs.email_notifications:
            reminder.channels.remove(NotificationChannelEnum.email)
        
        return len(reminder.channels) > 0
    
    @staticmethod
    async def _send_notification(reminder: TaskReminder) -> bool:
        """Send notification through specified channels"""
        success = True
        
        # Send browser notification (stored for frontend polling)
        if NotificationChannelEnum.browser in reminder.channels:
            await NotificationService._store_browser_notification(reminder)
        
        # Send email notification
        if NotificationChannelEnum.email in reminder.channels:
            email_success = await NotificationService._send_email_notification(reminder)
            success = success and email_success
        
        return success
    
    @staticmethod
    async def _store_browser_notification(reminder: TaskReminder) -> bool:
        """Store browser notification for frontend to retrieve"""
        notification_data = {
            "id": f"browser_{reminder.id}",
            "user_id": reminder.user_id,
            "type": "task_notification",
            "title": reminder.title,
            "message": reminder.message,
            "task_id": reminder.task_id,
            "task_name": reminder.task_name,
            "project_name": reminder.project_name,
            "priority": reminder.priority,
            "created_at": datetime.utcnow(),
            "read": False,
            "clicked": False
        }
        
        await create_document("browser_notifications", notification_data)
        return True
    
    @staticmethod
    async def _send_email_notification(reminder: TaskReminder) -> bool:
        """Send email notification"""
        try:
            # Get user details
            user_doc = await find_document("users", {"id": reminder.user_id})
            if not user_doc:
                logger.error(f"User not found for reminder {reminder.id}")
                return False
            
            user_email = user_doc["email"]
            user_name = f"{user_doc.get('first_name', '')} {user_doc.get('last_name', '')}".strip() or user_doc.get("username", "User")
            
            # Create email content
            subject = f"Aurum Life: {reminder.title}"
            
            # Create action URL based on notification type
            action_url = f"https://focus-planner-3.preview.emergentagent.com/tasks?task_id={reminder.task_id}"
            
            html_content = NotificationService._create_notification_email_template(
                user_name=user_name,
                title=reminder.title,
                message=reminder.message,
                task_name=reminder.task_name,
                project_name=reminder.project_name,
                priority=reminder.priority,
                action_url=action_url
            )
            
            return email_service.send_email(user_email, subject, html_content)
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False
    
    @staticmethod
    def _create_notification_email_template(user_name: str, title: str, message: str,
                                          task_name: Optional[str], project_name: Optional[str],
                                          priority: Optional[str], action_url: str) -> str:
        """Create HTML email template for notifications"""
        
        priority_color = {
            "high": "#dc2626",
            "medium": "#f59e0b", 
            "low": "#10b981"
        }.get(priority, "#6b7280")
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                body {{
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                    background-color: #0B0D14;
                    color: #ffffff;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #1a1d24;
                    border-radius: 12px;
                    padding: 40px;
                    margin-top: 20px;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    color: #F4B400;
                    font-size: 24px;
                    font-weight: bold;
                    margin-bottom: 10px;
                }}
                .title {{
                    color: #F4B400;
                    font-size: 24px;
                    font-weight: bold;
                    margin-bottom: 20px;
                }}
                .content {{
                    line-height: 1.6;
                    color: #e5e7eb;
                }}
                .task-info {{
                    background-color: #374151;
                    border-radius: 8px;
                    padding: 16px;
                    margin: 20px 0;
                }}
                .priority-badge {{
                    display: inline-block;
                    background-color: {priority_color};
                    color: white;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: 600;
                    text-transform: uppercase;
                }}
                .action-button {{
                    display: inline-block;
                    background-color: #F4B400;
                    color: #0B0D14;
                    text-decoration: none;
                    padding: 16px 32px;
                    border-radius: 8px;
                    font-weight: 600;
                    margin: 20px 0;
                    text-align: center;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #374151;
                    color: #9ca3af;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">Aurum Life</div>
                    <p style="color: #9ca3af;">Transform your potential into gold</p>
                </div>
                
                <div class="title">{title}</div>
                
                <div class="content">
                    <p>Hi {user_name},</p>
                    
                    <p>{message}</p>
                    
                    <div class="task-info">
                        <h3 style="margin-top: 0; color: #F4B400;">Task Details</h3>
                        <p><strong>Task:</strong> {task_name or 'Unknown Task'}</p>
                        {f'<p><strong>Project:</strong> {project_name}</p>' if project_name else ''}
                        {f'<p><strong>Priority:</strong> <span class="priority-badge">{priority}</span></p>' if priority else ''}
                    </div>
                    
                    <div style="text-align: center;">
                        <a href="{action_url}" class="action-button">View Task</a>
                    </div>
                    
                    <p>Stay focused and keep building your golden future! 🏆</p>
                </div>
                
                <div class="footer">
                    <p>You received this notification because you have task notifications enabled in your Aurum Life settings.</p>
                    <p>© 2025 Aurum Life - Personal Growth Platform</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    @staticmethod
    async def _handle_failed_notification(reminder: TaskReminder):
        """Handle failed notification with retry logic"""
        if reminder.retry_count < reminder.max_retries:
            next_retry = datetime.utcnow() + timedelta(minutes=5 * (reminder.retry_count + 1))
            await update_document("task_reminders",
                                {"id": reminder.id},
                                {
                                    "retry_count": reminder.retry_count + 1,
                                    "next_retry": next_retry
                                })
            logger.warning(f"Scheduling retry {reminder.retry_count + 1} for reminder {reminder.id}")
        else:
            logger.error(f"Max retries exceeded for reminder {reminder.id}")
    
    @staticmethod
    async def get_user_browser_notifications(user_id: str, unread_only: bool = False) -> List[Dict[str, Any]]:
        """Get browser notifications for a user"""
        query = {"user_id": user_id}
        if unread_only:
            query["read"] = False
        
        notifications = await find_documents("browser_notifications", query, sort=[("created_at", -1)], limit=50)
        return notifications
    
    @staticmethod
    async def mark_notification_read(user_id: str, notification_id: str) -> bool:
        """Mark a browser notification as read"""
        return await update_document("browser_notifications",
                                   {"id": notification_id, "user_id": user_id},
                                   {"read": True})
    
    @staticmethod
    async def mark_all_notifications_read(user_id: str) -> int:
        """Mark all browser notifications as read for a user"""
        try:
            query = {"user_id": user_id, "read": False}
            update = {"read": True}
            return await bulk_update_documents("browser_notifications", query, update)
        except Exception as e:
            logger.error(f"Error marking notifications as read for user {user_id}: {e}")
            return 0
    
    @staticmethod
    async def delete_notification(user_id: str, notification_id: str) -> bool:
        """Delete a specific browser notification"""
        return await delete_document("browser_notifications",
                                   {"id": notification_id, "user_id": user_id})
    
    @staticmethod
    async def clear_all_notifications(user_id: str) -> int:
        """Clear all browser notifications for a user"""
        try:
            query = {"user_id": user_id}
            return await bulk_delete_documents("browser_notifications", query)
        except Exception as e:
            logger.error(f"Error clearing notifications for user {user_id}: {e}")
            return 0
    
    @staticmethod
    async def schedule_task_reminders_for_task(user_id: str, task_id: str, task_name: str, 
                                             due_date: datetime, due_time: Optional[str] = None,
                                             project_name: Optional[str] = None) -> List[str]:
        """Schedule all appropriate reminders for a task based on user preferences"""
        prefs = await NotificationService.get_user_notification_preferences(user_id)
        if not prefs:
            prefs = await NotificationService.create_default_notification_preferences(user_id)
        
        reminder_ids = []
        
        # Calculate due datetime
        if due_time:
            try:
                hour, minute = map(int, due_time.split(':'))
                due_datetime = due_date.replace(hour=hour, minute=minute)
            except:
                due_datetime = due_date
        else:
            due_datetime = due_date
        
        # Schedule advance reminder
        if prefs.task_reminder_notifications and prefs.reminder_advance_time > 0:
            reminder_time = due_datetime - timedelta(minutes=prefs.reminder_advance_time)
            if reminder_time > datetime.utcnow():
                title = f"Task Due Soon: {task_name}"
                message = f"Your task '{task_name}' is due in {prefs.reminder_advance_time} minutes."
                if project_name:
                    message += f" (Project: {project_name})"
                
                reminder_id = await NotificationService.schedule_task_reminder(
                    user_id=user_id,
                    task_id=task_id,
                    notification_type=NotificationTypeEnum.task_reminder,
                    scheduled_time=reminder_time,
                    title=title,
                    message=message,
                    channels=[NotificationChannelEnum.browser, NotificationChannelEnum.email] if prefs.email_notifications else [NotificationChannelEnum.browser]
                )
                reminder_ids.append(reminder_id)
        
        # Schedule due notification
        if prefs.task_due_notifications:
            title = f"Task Due Now: {task_name}"
            message = f"Your task '{task_name}' is due now."
            if project_name:
                message += f" (Project: {project_name})"
            
            reminder_id = await NotificationService.schedule_task_reminder(
                user_id=user_id,
                task_id=task_id,
                notification_type=NotificationTypeEnum.task_due,
                scheduled_time=due_datetime,
                title=title,
                message=message,
                channels=[NotificationChannelEnum.browser]
            )
            reminder_ids.append(reminder_id)
        
        return reminder_ids
    
    @staticmethod
    async def check_overdue_tasks() -> int:
        """Check for overdue tasks and send notifications"""
        now = datetime.utcnow()
        
        # Find all active tasks that are overdue
        overdue_tasks = await find_documents("tasks", {
            "completed": False,
            "due_date": {"$lt": now}
        })
        
        notifications_sent = 0
        
        for task_doc in overdue_tasks:
            try:
                task = Task(**task_doc)
                
                # Check if we already sent an overdue notification recently
                recent_overdue = await find_document("task_reminders", {
                    "task_id": task.id,
                    "notification_type": NotificationTypeEnum.task_overdue,
                    "sent_at": {"$gte": now - timedelta(hours=1)}  # Don't spam - only once per hour
                })
                
                if recent_overdue:
                    continue
                
                # Get project name
                project_doc = await find_document("projects", {"id": task.project_id})
                project_name = project_doc["name"] if project_doc else None
                
                # Schedule overdue notification
                title = f"Overdue Task: {task.name}"
                message = f"Your task '{task.name}' is overdue. Please review and update it."
                if project_name:
                    message += f" (Project: {project_name})"
                
                await NotificationService.schedule_task_reminder(
                    user_id=task.user_id,
                    task_id=task.id,
                    notification_type=NotificationTypeEnum.task_overdue,
                    scheduled_time=now,
                    title=title,
                    message=message,
                    channels=[NotificationChannelEnum.browser, NotificationChannelEnum.email]
                )
                
                notifications_sent += 1
                
            except Exception as e:
                logger.error(f"Error processing overdue task {task_doc.get('id')}: {e}")
        
        return notifications_sent

    @staticmethod
    async def create_notification(notification_data: dict) -> Optional[BrowserNotification]:
        """Create a browser notification"""
        try:
            # Add timestamp and ID if not provided
            if "id" not in notification_data:
                from uuid import uuid4
                notification_data["id"] = str(uuid4())
            if "created_at" not in notification_data:
                notification_data["created_at"] = datetime.utcnow()
            if "updated_at" not in notification_data:
                notification_data["updated_at"] = datetime.utcnow()
            
            # Create the notification document
            await create_document("browser_notifications", notification_data)
            
            # Return as BrowserNotification object
            return BrowserNotification(**notification_data)
            
        except Exception as e:
            logger.error(f"Error creating browser notification: {e}")
            return None
    
    @staticmethod
    async def get_user_browser_notifications(user_id: str, unread_only: bool = False) -> List[dict]:
        """Get browser notifications for a user"""
        try:
            filter_criteria = {"user_id": user_id}
            if unread_only:
                filter_criteria["is_read"] = False
            
            notifications = await find_documents("browser_notifications", filter_criteria)
            
            # Sort by created_at descending (newest first)
            notifications = sorted(notifications, key=lambda x: x.get('created_at', datetime.min), reverse=True)
            
            return notifications
            
        except Exception as e:
            logger.error(f"Error getting browser notifications for user {user_id}: {e}")
            return []
    
    @staticmethod
    async def mark_notification_read(user_id: str, notification_id: str) -> bool:
        """Mark a notification as read"""
        try:
            success = await update_document(
                "browser_notifications",
                {"id": notification_id, "user_id": user_id},
                {
                    "is_read": True,
                    "read_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            )
            return success
            
        except Exception as e:
            logger.error(f"Error marking notification {notification_id} as read: {e}")
            return False
    
    @staticmethod
    async def mark_all_notifications_read(user_id: str) -> int:
        """Mark all notifications as read for a user"""
        try:
            # Get all unread notifications
            unread_notifications = await find_documents("browser_notifications", {
                "user_id": user_id,
                "is_read": False
            })
            
            count = 0
            for notification in unread_notifications:
                success = await update_document(
                    "browser_notifications",
                    {"id": notification["id"], "user_id": user_id},
                    {
                        "is_read": True,
                        "read_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                )
                if success:
                    count += 1
            
            return count
            
        except Exception as e:
            logger.error(f"Error marking all notifications as read for user {user_id}: {e}")
            return 0
    
    @staticmethod
    async def delete_notification(user_id: str, notification_id: str) -> bool:
        """Delete a specific notification"""
        try:
            success = await delete_document("browser_notifications", {
                "id": notification_id,
                "user_id": user_id
            })
            return success
            
        except Exception as e:
            logger.error(f"Error deleting notification {notification_id}: {e}")
            return False
    
# Create global notification service instance
notification_service = NotificationService()