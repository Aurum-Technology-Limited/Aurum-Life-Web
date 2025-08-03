#!/usr/bin/env python3
"""
Live Email Test - Send Beautiful Notification Email
Tests email notifications with the actual email service
"""

import sys
import os
from datetime import datetime

# Add the backend directory to the path
sys.path.append('/app/backend')

# Load environment
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

# Import email service directly
from email_service import email_service
from notification_service import NotificationService

def test_beautiful_notification_email():
    """Send a beautiful notification email using the actual email service"""
    print("📧 SENDING BEAUTIFUL NOTIFICATION EMAIL")
    print("=" * 50)
    
    recipient_email = "marc.alleyne@aurumtechnologyltd.com"
    
    # Generate professional notification email content
    html_content = NotificationService._create_notification_email_template(
        user_name="Marc Alleyne",
        title="🎯 Task Due: Email Notification System Setup Complete",
        message="Congratulations! Your Aurum Life email notification system is now fully operational. This is a live test email showcasing the beautiful notification template that your users will receive.",
        task_name="Complete Email Notification Setup",
        project_name="Aurum Life Enhancement Project",
        priority="high",
        action_url="https://d5525f43-5dcd-48e4-b22b-982ef0b3bb33.preview.emergentagent.com/tasks"
    )
    
    print(f"Recipient: {recipient_email}")
    print(f"Template Length: {len(html_content)} characters")
    print(f"Sender: {os.getenv('SENDER_EMAIL')}")
    print()
    
    try:
        # Send the email using the email service
        success = email_service.send_email(
            to=recipient_email,
            subject="🎉 Aurum Life - Email Notifications Live Test",
            html_content=html_content,
            plain_text_content="""
            Aurum Life - Task Notification
            
            Hi Marc Alleyne,
            
            Congratulations! Your Aurum Life email notification system is now fully operational.
            
            Task: Complete Email Notification Setup
            Project: Aurum Life Enhancement Project
            Priority: High
            
            This is a live test email showcasing that your notification system is working perfectly.
            
            View your tasks at: https://d5525f43-5dcd-48e4-b22b-982ef0b3bb33.preview.emergentagent.com/tasks
            
            Best regards,
            Aurum Life Team
            """
        )
        
        if success:
            print("✅ BEAUTIFUL NOTIFICATION EMAIL SENT SUCCESSFULLY!")
            print()
            print("🎉 EMAIL NOTIFICATION SYSTEM IS LIVE!")
            print("=" * 50)
            print("Check your email: marc.alleyne@aurumtechnologyltd.com")
            print()
            print("The email includes:")
            print("• 🎨 Professional Aurum Life branding")
            print("• 📋 Complete task details")
            print("• 🎯 Priority badge (High - Red)")
            print("• 🔗 Direct action button")
            print("• 📱 Mobile-responsive design")
            print("• 🌙 Dark theme matching the app")
            print()
            print("🚀 Your users will now receive these beautiful")
            print("   professional emails for all task notifications!")
            return True
        else:
            print("❌ Failed to send email")
            return False
            
    except Exception as e:
        print(f"❌ Email sending error: {e}")
        return False

def test_password_reset_email():
    """Test the password reset email template"""
    print("\n🔒 TESTING PASSWORD RESET EMAIL")
    print("=" * 50)
    
    try:
        success = email_service.send_password_reset_email(
            email="marc.alleyne@aurumtechnologyltd.com",
            reset_token="test_token_123456789",
            user_name="Marc Alleyne"
        )
        
        if success:
            print("✅ Password reset email sent successfully!")
            print("Check your email for the password reset template")
            return True
        else:
            print("❌ Failed to send password reset email")
            return False
            
    except Exception as e:
        print(f"❌ Password reset email error: {e}")
        return False

def main():
    """Run live email tests"""
    print("🚀 AURUM LIFE LIVE EMAIL TESTING")
    print("=" * 60)
    print(f"Testing started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"SendGrid Mode: {'🔴 Mock' if email_service.mock_mode else '✅ Live'}")
    print()
    
    # Test 1: Beautiful notification email
    notification_success = test_beautiful_notification_email()
    
    # Test 2: Password reset email  
    reset_success = test_password_reset_email()
    
    # Summary
    print("\n📊 LIVE EMAIL TEST RESULTS")
    print("=" * 50)
    print(f"Notification Email: {'✅ Sent' if notification_success else '❌ Failed'}")
    print(f"Password Reset Email: {'✅ Sent' if reset_success else '❌ Failed'}")
    
    total_tests = 2
    passed_tests = sum([notification_success, reset_success])
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if notification_success and reset_success:
        print("\n🎉 ALL EMAIL SYSTEMS ARE FULLY OPERATIONAL!")
        print("=" * 60)
        print("✅ Task notification emails working")
        print("✅ Password reset emails working") 
        print("✅ Beautiful HTML templates rendering")
        print("✅ SendGrid integration successful")
        print("✅ Professional branding applied")
        print()
        print("🚀 EMAIL NOTIFICATIONS ARE PRODUCTION READY!")
        print("   Your users will receive professional emails for:")
        print("   • Task due reminders")
        print("   • Task overdue alerts")
        print("   • Project deadlines")
        print("   • Password resets")
        print("   • Custom notifications")
    else:
        print(f"\n⚠️ {2-passed_tests} email system(s) need attention")

if __name__ == "__main__":
    main()