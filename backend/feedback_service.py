"""
Feedback Service - Handles feedback database operations and email notifications
"""

import os
from datetime import datetime
from typing import Dict, List, Optional
from supabase import create_client, Client
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

logger = logging.getLogger(__name__)

class FeedbackService:
    def __init__(self):
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
        if not supabase_url or not supabase_key:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY environment variables")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)

    async def create_feedback(self, user_id: str, user_email: str, user_name: str, feedback_data: Dict) -> Dict:
        """
        Create a new feedback entry and send email notification
        """
        try:
            # Create feedback record
            feedback = {
                'user_id': user_id,
                'user_email': user_email,
                'user_name': user_name,
                'category': feedback_data.category,
                'priority': feedback_data.priority,
                'subject': feedback_data.subject,
                'message': feedback_data.message,
                'status': 'open',
                'email_sent': False,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Insert into database
            response = self.supabase.table('feedback').insert(feedback).execute()
            
            if not response.data:
                logger.error("Failed to create feedback record")
                return None
            
            feedback_record = response.data[0]
            logger.info(f"Feedback record created with ID: {feedback_record['id']}")
            
            # Send email notification
            try:
                await self._send_feedback_email(feedback_record)
                
                # Update email sent status
                self.supabase.table('feedback').update({
                    'email_sent': True,
                    'email_sent_at': datetime.utcnow().isoformat()
                }).eq('id', feedback_record['id']).execute()
                
            except Exception as email_error:
                logger.error(f"Failed to send feedback email: {email_error}")
                
                # Update with email error
                self.supabase.table('feedback').update({
                    'email_error': str(email_error)
                }).eq('id', feedback_record['id']).execute()
            
            return feedback_record
            
        except Exception as e:
            logger.error(f"Error creating feedback: {e}")
            return None

    async def _send_feedback_email(self, feedback_record: Dict):
        """
        Send formatted feedback email to admin
        """
        # Admin email - get from environment or use sender email
        admin_email = os.getenv('ADMIN_EMAIL', os.getenv('SENDER_EMAIL'))
        
        if not admin_email:
            raise Exception("No admin email configured for feedback notifications")
        
        # Format category for display
        category_labels = {
            'suggestion': 'Suggestion',
            'bug_report': 'Bug Report',
            'feature_request': 'Feature Request',
            'question': 'Question',
            'complaint': 'Complaint',
            'compliment': 'Compliment'
        }
        
        category_label = category_labels.get(feedback_record['category'], 'Feedback')
        priority_label = feedback_record['priority'].title()
        
        subject = f"Aurum Life Feedback: {category_label} - {feedback_record['subject']}"
        
        # Create HTML email content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>New Feedback - Aurum Life</title>
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
                    font-size: 22px;
                    font-weight: bold;
                    margin-bottom: 20px;
                }}
                .content {{
                    line-height: 1.6;
                    color: #e5e7eb;
                }}
                .feedback-details {{
                    background-color: #374151;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px 0;
                }}
                .detail-row {{
                    display: flex;
                    margin-bottom: 10px;
                }}
                .detail-label {{
                    font-weight: bold;
                    color: #F4B400;
                    min-width: 120px;
                }}
                .detail-value {{
                    color: #e5e7eb;
                }}
                .message-content {{
                    background-color: #4B5563;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px 0;
                    white-space: pre-wrap;
                    border-left: 4px solid #F4B400;
                }}
                .priority-high {{
                    color: #EF4444;
                    font-weight: bold;
                }}
                .priority-urgent {{
                    color: #DC2626;
                    font-weight: bold;
                    background-color: #FEE2E2;
                    padding: 2px 8px;
                    border-radius: 4px;
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
                    <p style="color: #9ca3af;">Feedback Management System</p>
                </div>
                
                <div class="title">New Feedback Received</div>
                
                <div class="content">
                    <p>You've received new feedback from an Aurum Life user:</p>
                    
                    <div class="feedback-details">
                        <div class="detail-row">
                            <span class="detail-label">Type:</span>
                            <span class="detail-value">{category_label}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Priority:</span>
                            <span class="detail-value {'priority-' + feedback_record['priority']}">{priority_label}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Subject:</span>
                            <span class="detail-value">{feedback_record['subject']}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">User:</span>
                            <span class="detail-value">{feedback_record['user_name']} ({feedback_record['user_email']})</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">User ID:</span>
                            <span class="detail-value">{feedback_record['user_id']}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Submitted:</span>
                            <span class="detail-value">{feedback_record['created_at']}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Feedback ID:</span>
                            <span class="detail-value">{feedback_record['id']}</span>
                        </div>
                    </div>
                    
                    <h3 style="color: #F4B400;">Message:</h3>
                    <div class="message-content">{feedback_record['message']}</div>
                    
                    <p>This feedback was submitted through the Aurum Life application and has been saved to the database for your review.</p>
                </div>
                
                <div class="footer">
                    <p>This email was sent from the Aurum Life feedback system.</p>
                    <p>© 2025 Aurum Life - Personal Growth Platform</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create plain text version
        plain_text_content = f"""
        Aurum Life - New Feedback Received
        
        Type: {category_label}
        Priority: {priority_label}
        Subject: {feedback_record['subject']}
        User: {feedback_record['user_name']} ({feedback_record['user_email']})
        User ID: {feedback_record['user_id']}
        Submitted: {feedback_record['created_at']}
        Feedback ID: {feedback_record['id']}
        
        Message:
        {feedback_record['message']}
        
        This feedback was submitted through the Aurum Life application.
        
        © 2025 Aurum Life - Personal Growth Platform
        """
        
        # Send email
        success = self._send_email(
            to=admin_email,
            subject=subject,
            html_content=html_content,
            plain_text_content=plain_text_content
        )
        
        if not success:
            raise Exception("Failed to send feedback notification email")
        
        logger.info(f"Feedback notification email sent to {admin_email}")

    async def get_user_feedback(self, user_id: str, limit: int = 50) -> List[Dict]:
        """
        Get user's feedback history
        """
        try:
            response = self.supabase.table('feedback')\
                .select('*')\
                .eq('user_id', user_id)\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data or []
            
        except Exception as e:
            logger.error(f"Error fetching user feedback: {e}")
            return []

    async def get_all_feedback(self, status: Optional[str] = None, category: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """
        Get all feedback (for admin use)
        """
        try:
            query = self.supabase.table('feedback').select('*')
            
            if status:
                query = query.eq('status', status)
            if category:
                query = query.eq('category', category)
            
            response = query.order('created_at', desc=True).limit(limit).execute()
            
            return response.data or []
            
        except Exception as e:
            logger.error(f"Error fetching all feedback: {e}")
            return []

# Create global feedback service instance
feedback_service = FeedbackService()