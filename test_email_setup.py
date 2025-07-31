#!/usr/bin/env python3
"""
Email Notification Setup Testing Script
Tests email configuration and sends test notifications
"""

import sys
import os
import asyncio
from datetime import datetime

# Add the backend directory to the path
sys.path.append('/app/backend')

from email_service import email_service
from notification_service import NotificationService
from models import TaskReminder, NotificationTypeEnum, NotificationChannelEnum, PriorityEnum

async def test_email_configuration():
    """Test basic email service configuration"""
    print("🔧 TESTING EMAIL CONFIGURATION")
    print("=" * 50)
    
    # Check environment variables
    sendgrid_key = os.getenv('SENDGRID_API_KEY')
    sender_email = os.getenv('SENDER_EMAIL')
    
    print(f"SendGrid API Key: {'✅ Configured' if sendgrid_key and sendgrid_key != 'your_sendgrid_api_key_here' else '❌ Not configured'}")
    print(f"Sender Email: {sender_email}")
    print(f"Mock Mode: {'✅ Active (Development)' if email_service.mock_mode else '❌ Live Mode (Production)'}")
    
    return not email_service.mock_mode

def test_basic_email_sending():
    """Test basic email sending functionality"""
    print("\n📧 TESTING BASIC EMAIL SENDING")
    print("=" * 50)
    
    test_recipient = "test@example.com"  # Change this to your email for testing
    
    try:
        success = email_service.send_email(
            to=test_recipient,
            subject="Aurum Life - Email Test",
            html_content="""
            <h2>🎉 Email Configuration Test</h2>
            <p>If you're reading this, your email notifications are working perfectly!</p>
            <p>This is a test email from your Aurum Life application.</p>
            <p><strong>Time sent:</strong> {}</p>
            """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            plain_text_content="Email Configuration Test - If you're reading this, your email notifications are working!"
        )
        
        print(f"✅ Basic email test: {'Success' if success else 'Failed'}")
        return success
        
    except Exception as e:
        print(f"❌ Basic email test failed: {e}")
        return False

async def test_notification_email_template():
    """Test notification email template generation"""
    print("\n🎨 TESTING NOTIFICATION EMAIL TEMPLATE")
    print("=" * 50)
    
    # Create a sample task reminder
    sample_reminder = TaskReminder(
        id="test_reminder_123",
        user_id="test_user_456", 
        task_id="test_task_789",
        notification_type=NotificationTypeEnum.task_due,
        scheduled_time=datetime.now(),
        title="Test Task Due Reminder",
        message="This is a test notification for your task reminder system.",
        task_name="Complete Email Setup",
        project_name="Aurum Life Enhancement",
        priority=PriorityEnum.high,
        channels=[NotificationChannelEnum.email]
    )
    
    # Generate email template
    html_content = NotificationService._create_notification_email_template(
        user_name="Test User",
        title=sample_reminder.title,
        message=sample_reminder.message,
        task_name=sample_reminder.task_name,
        project_name=sample_reminder.project_name,
        priority="high",
        action_url="https://7767cc54-7d42-422d-ae92-93a862d5b150.preview.emergentagent.com/tasks"
    )
    
    print("✅ Email template generated successfully")
    print(f"Template length: {len(html_content)} characters")
    
    # Save template to file for inspection
    with open('/tmp/sample_notification_email.html', 'w') as f:
        f.write(html_content)
    print("✅ Sample email template saved to /tmp/sample_notification_email.html")
    
    return True

def test_send_sample_notification_email():
    """Send a complete sample notification email"""
    print("\n📬 TESTING COMPLETE NOTIFICATION EMAIL")
    print("=" * 50)
    
    test_recipient = "test@example.com"  # Change this to your email for testing
    
    html_content = NotificationService._create_notification_email_template(
        user_name="Test User",
        title="Task Due Reminder - Email Test",
        message="This is a complete test of your task notification email system.",
        task_name="Set up Email Notifications",
        project_name="Aurum Life Configuration",
        priority="high",
        action_url="https://7767cc54-7d42-422d-ae92-93a862d5b150.preview.emergentagent.com/tasks"
    )
    
    try:
        success = email_service.send_email(
            to=test_recipient,
            subject="Aurum Life - Task Notification Test",
            html_content=html_content,
            plain_text_content="This is a test notification email from Aurum Life."
        )
        
        print(f"✅ Complete notification email test: {'Success' if success else 'Failed'}")
        return success
        
    except Exception as e:
        print(f"❌ Complete notification email test failed: {e}")
        return False

async def main():
    """Run all email setup tests"""
    print("🚀 AURUM LIFE EMAIL NOTIFICATION SETUP TESTING")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: Configuration
    email_configured = await test_email_configuration()
    
    # Test 2: Basic email sending
    basic_email_works = test_basic_email_sending()
    
    # Test 3: Email template generation
    template_works = await test_notification_email_template()
    
    # Test 4: Complete notification email
    notification_email_works = test_send_sample_notification_email()
    
    # Summary
    print("\n📊 TESTING SUMMARY")
    print("=" * 50)
    print(f"Configuration: {'✅ Ready' if email_configured else '⚠️ Mock Mode'}")
    print(f"Basic Email: {'✅ Working' if basic_email_works else '❌ Failed'}")
    print(f"Template Generation: {'✅ Working' if template_works else '❌ Failed'}")  
    print(f"Notification Email: {'✅ Working' if notification_email_works else '❌ Failed'}")
    
    total_tests = 4
    passed_tests = sum([email_configured, basic_email_works, template_works, notification_email_works])
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests)*100:.1f}%)")
    
    if email_configured and basic_email_works:
        print("\n🎉 EMAIL NOTIFICATIONS ARE READY FOR PRODUCTION!")
    elif basic_email_works:
        print("\n⚠️ EMAIL NOTIFICATIONS WORKING IN MOCK MODE")
        print("   Configure SENDGRID_API_KEY in .env for production")
    else:
        print("\n❌ EMAIL NOTIFICATIONS NEED CONFIGURATION")
        print("   Please check your SendGrid setup and API key")

if __name__ == "__main__":
    asyncio.run(main())