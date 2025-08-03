#!/usr/bin/env python3
"""
Email Delivery Test Script for Outlook
Tests SendGrid configuration and provides delivery diagnostics
"""

import os
import sys
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import json

def test_sendgrid_setup():
    """Test SendGrid configuration"""
    print("🔍 Testing SendGrid Configuration...")
    
    load_dotenv()
    api_key = os.getenv('SENDGRID_API_KEY')
    sender_email = os.getenv('SENDER_EMAIL')
    
    print(f"✅ SendGrid API Key: {'Present' if api_key else 'Missing'}")
    print(f"✅ Sender Email: {sender_email}")
    
    if not api_key:
        print("❌ SendGrid API key not found!")
        return False
    
    try:
        client = SendGridAPIClient(api_key)
        print("✅ SendGrid client initialized successfully")
        return True, client, sender_email
    except Exception as e:
        print(f"❌ SendGrid client error: {e}")
        return False

def send_test_email(recipient_email: str):
    """Send a simple test email"""
    result = test_sendgrid_setup()
    if not result:
        return False
        
    success, client, sender_email = result
    
    print(f"\n📧 Sending test email to: {recipient_email}")
    
    # Simple, Outlook-friendly test email
    message = Mail(
        from_email=sender_email,
        to_emails=recipient_email,
        subject="[Test] Aurum Life Email Delivery Test",
        html_content="""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h2 style="color: #F4B400;">Aurum Life Email Test</h2>
            <p>This is a test email to verify delivery to your Outlook inbox.</p>
            <p><strong>If you receive this email:</strong></p>
            <ul>
                <li>Check if it arrived in your Inbox or Spam/Junk folder</li>
                <li>Note the time you received it</li>
                <li>Mark it as "Not Junk" if it's in spam</li>
            </ul>
            <p>Best regards,<br>Aurum Life System</p>
        </body>
        </html>
        """,
        plain_text_content="""
Aurum Life Email Test

This is a test email to verify delivery to your Outlook inbox.

If you receive this email:
- Check if it arrived in your Inbox or Spam/Junk folder
- Note the time you received it
- Mark it as "Not Junk" if it's in spam

Best regards,
Aurum Life System
        """
    )
    
    # Add Outlook-friendly headers
    message.header = {
        "X-Priority": "3",
        "X-Mailer": "Aurum Life Test",
        "Precedence": "bulk"
    }
    
    try:
        response = client.send(message)
        
        print(f"📬 SendGrid Response Status: {response.status_code}")
        print(f"📬 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 202:
            print("✅ Email accepted by SendGrid for delivery!")
            print("⏰ Check your Outlook inbox and spam folder in 1-2 minutes")
            return True
        else:
            print(f"❌ SendGrid rejected email: {response.status_code}")
            print(f"❌ Response body: {response.body}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

def check_domain_authentication():
    """Check domain authentication status"""
    result = test_sendgrid_setup()
    if not result:
        return
        
    success, client, sender_email = result
    domain = sender_email.split('@')[1]
    
    print(f"\n🔐 Domain Authentication Check for: {domain}")
    print("To fix Outlook delivery issues:")
    print("1. Log into SendGrid Dashboard")
    print("2. Go to Settings > Sender Authentication")
    print("3. Authenticate your domain with DNS records")
    print("4. Or use a SendGrid-verified domain temporarily")
    
    print(f"\n💡 Quick Fix: Try changing SENDER_EMAIL to use @sendgrid.net domain")

if __name__ == "__main__":
    print("🚀 Aurum Life Email Delivery Diagnostic Tool")
    print("=" * 50)
    
    if len(sys.argv) != 2:
        print("Usage: python test_email_delivery.py your-email@outlook.com")
        sys.exit(1)
    
    recipient = sys.argv[1]
    print(f"Testing email delivery to: {recipient}")
    
    # Run diagnostics
    send_test_email(recipient)
    check_domain_authentication()