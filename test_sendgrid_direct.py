#!/usr/bin/env python3
"""
Direct SendGrid API Test
Tests the SendGrid API key directly with real email sending
"""

import os
import sys
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Load environment variables
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

def test_sendgrid_direct():
    """Test SendGrid API directly"""
    print("🔧 DIRECT SENDGRID API TEST")
    print("=" * 50)
    
    # Get API key from environment
    api_key = os.getenv('SENDGRID_API_KEY')
    sender_email = os.getenv('SENDER_EMAIL', 'notifications@aurumlife.com')
    
    print(f"API Key: {api_key[:20]}..." if api_key else "None")
    print(f"Sender Email: {sender_email}")
    
    if not api_key or api_key == 'your_sendgrid_api_key_here':
        print("❌ SendGrid API key not configured properly")
        return False
    
    try:
        # Initialize SendGrid client
        sg = SendGridAPIClient(api_key)
        
        # Create test email
        message = Mail(
            from_email=sender_email,
            to_emails='test@example.com',  # Change this to your email for real testing
            subject='Aurum Life - SendGrid API Test',
            html_content='''
            <h2>🎉 SendGrid API Test Successful!</h2>
            <p>If you're reading this email, your SendGrid integration is working perfectly!</p>
            <p>Your Aurum Life email notifications are now fully operational.</p>
            <p><strong>Test completed at:</strong> ''' + str(os.popen('date').read().strip()) + '''</p>
            '''
        )
        
        # Send email
        response = sg.send(message)
        
        print(f"✅ SendGrid API Response: {response.status_code}")
        print(f"✅ Response Headers: {dict(response.headers)}")
        
        if response.status_code == 202:
            print("🎉 EMAIL SENT SUCCESSFULLY!")
            print("✅ SendGrid API is working correctly")
            print("✅ Email notifications are now LIVE!")
            return True
        else:
            print(f"⚠️ Unexpected response code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ SendGrid API Error: {e}")
        return False

if __name__ == "__main__":
    success = test_sendgrid_direct()
    if success:
        print("\n🚀 YOUR EMAIL NOTIFICATIONS ARE LIVE!")
        print("Users will now receive real email notifications for:")
        print("• Task due reminders")
        print("• Task overdue alerts") 
        print("• Project deadlines")
        print("• Custom task reminders")
    else:
        print("\n❌ Email setup needs attention")
        print("Please check your SendGrid API key and configuration")