"""
SendGrid Email Service for Aurum Life
Handles password reset emails and other notifications
"""

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class EmailDeliveryError(Exception):
    """Raised when email delivery fails"""
    pass

class EmailService:
    def __init__(self):
        # Force reload of environment variables
        from dotenv import load_dotenv
        from pathlib import Path
        ROOT_DIR = Path(__file__).parent
        load_dotenv(ROOT_DIR / '.env')
        
        self.api_key = os.getenv('SENDGRID_API_KEY')
        self.sender_email = os.getenv('SENDER_EMAIL')
        
        # Debug logging
        logger.info(f"EmailService initialization:")
        logger.info(f"  SENDGRID_API_KEY present: {bool(self.api_key)}")
        logger.info(f"  SENDGRID_API_KEY first 10 chars: {self.api_key[:10] if self.api_key else 'None'}")
        logger.info(f"  SENDER_EMAIL: {self.sender_email}")
        
        if not self.api_key or self.api_key == 'your_sendgrid_api_key_here':
            logger.warning("SendGrid API key not configured. Email functionality will be mocked.")
            self.mock_mode = True
        else:
            logger.info("SendGrid API key configured. Email functionality will use SendGrid.")
            self.mock_mode = False
            self.client = SendGridAPIClient(self.api_key)

    def send_email(self, to: str, subject: str, html_content: str, plain_text_content: Optional[str] = None):
        """
        Send email via SendGrid or mock for development
        
        Args:
            to: Recipient email address
            subject: Email subject line
            html_content: HTML email content
            plain_text_content: Plain text version (optional)
        
        Returns:
            bool: True if email was sent successfully
        """
        if self.mock_mode:
            return self._send_mock_email(to, subject, html_content)
        
        try:
            message = Mail(
                from_email=self.sender_email,
                to_emails=to,
                subject=subject,
                html_content=html_content,
                plain_text_content=plain_text_content
            )
            
            response = self.client.send(message)
            
            if response.status_code == 202:
                logger.info(f"Password reset email sent successfully to {to}")
                return True
            else:
                logger.error(f"SendGrid returned status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send email to {to}: {str(e)}")
            raise EmailDeliveryError(f"Failed to send email: {str(e)}")

    def _send_mock_email(self, to: str, subject: str, content: str) -> bool:
        """
        Mock email sending for development/testing
        """
        logger.info(f"[MOCK EMAIL] To: {to}")
        logger.info(f"[MOCK EMAIL] Subject: {subject}")
        logger.info(f"[MOCK EMAIL] Content Preview: {content[:100]}...")
        print(f"\n🔥 MOCK EMAIL SENT 🔥")
        print(f"To: {to}")
        print(f"Subject: {subject}")
        print(f"Content: {content}")
        print("=" * 50)
        return True

    async def send_password_reset_email(self, email: str, reset_token: str, user_name: str = "User"):
        """
        Send password reset email with secure reset link
        
        Args:
            email: User's email address
            reset_token: Secure reset token
            user_name: User's first name or username
        """
        # Use the correct frontend URL for password reset
        frontend_url = os.getenv('FRONTEND_URL', 'https://8f43b565-3ef8-487e-92ed-bb0b1b3a1936.preview.emergentagent.com')
        reset_url = f"{frontend_url}/reset-password?token={reset_token}"
        
        subject = "Reset Your Aurum Life Password"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reset Your Password</title>
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
                .reset-button {{
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
                .warning {{
                    background-color: #dc2626;
                    color: white;
                    padding: 12px;
                    border-radius: 6px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">Aurum Life</div>
                    <p style="color: #9ca3af;">Transform your potential into gold</p>
                </div>
                
                <div class="title">Password Reset Request</div>
                
                <div class="content">
                    <p>Hi {user_name},</p>
                    
                    <p>We received a request to reset your password for your Aurum Life account. If you made this request, click the button below to create a new password:</p>
                    
                    <div style="text-align: center;">
                        <a href="{reset_url}" class="reset-button">Reset Password</a>
                    </div>
                    
                    <div class="warning">
                        <strong>⚠️ Security Notice:</strong> This link will expire in 24 hours for your security. If you didn't request this password reset, please ignore this email.
                    </div>
                    
                    <p>If the button above doesn't work, you can copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #F4B400;">{reset_url}</p>
                    
                    <p>For security reasons, we'll never ask for your password via email. If you have any concerns about this email, please contact our support team.</p>
                </div>
                
                <div class="footer">
                    <p>This email was sent from Aurum Life. If you didn't request this password reset, you can safely ignore this email.</p>
                    <p>© 2025 Aurum Life - Personal Growth Platform</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        plain_text_content = f"""
        Aurum Life - Password Reset Request
        
        Hi {user_name},
        
        We received a request to reset your password for your Aurum Life account.
        
        To reset your password, visit this link: {reset_url}
        
        SECURITY NOTICE: This link will expire in 24 hours for your security.
        If you didn't request this password reset, please ignore this email.
        
        For security reasons, we'll never ask for your password via email.
        
        © 2025 Aurum Life - Personal Growth Platform
        """
        
        return self.send_email(email, subject, html_content, plain_text_content)

# Create global email service instance
email_service = EmailService()