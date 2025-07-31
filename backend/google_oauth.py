"""
Google OAuth 2.0 Authentication Service
Direct integration with Google Cloud Platform OAuth services
"""

import os
import uuid
import json
import requests
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import logging

logger = logging.getLogger(__name__)

class GoogleOAuthService:
    """Service for handling Google OAuth 2.0 authentication"""
    
    def __init__(self):
        self.client_id = os.getenv('GOOGLE_CLIENT_ID')
        self.client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        self.redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8001/api/auth/google/callback')
        
        if not self.client_id or not self.client_secret:
            raise ValueError("Google OAuth credentials not found in environment variables")
    
    def get_authorization_url(self, state: str = None) -> str:
        """
        Generate Google OAuth authorization URL
        
        Args:
            state: Optional state parameter for CSRF protection
            
        Returns:
            Google OAuth authorization URL
        """
        if not state:
            state = str(uuid.uuid4())
            
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'scope': 'openid email profile',
            'redirect_uri': self.redirect_uri,
            'state': state,
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{query_string}"
        
        logger.info(f"Generated Google OAuth URL for state: {state}")
        return auth_url
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token
        
        Args:
            code: Authorization code from Google
            
        Returns:
            Token response from Google
        """
        try:
            token_url = "https://oauth2.googleapis.com/token"
            
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': self.redirect_uri
            }
            
            response = requests.post(token_url, data=data)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Token exchange failed: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange code for token"
                )
                
        except requests.RequestException as e:
            logger.error(f"Network error during token exchange: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service temporarily unavailable"
            )
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Get user information from Google using access token
        
        Args:
            access_token: Access token from Google
            
        Returns:
            User information from Google
        """
        try:
            user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
            headers = {'Authorization': f'Bearer {access_token}'}
            
            response = requests.get(user_info_url, headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                logger.info(f"Retrieved user info for: {user_data.get('email')}")
                return user_data
            else:
                logger.error(f"Failed to get user info: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to retrieve user information"
                )
                
        except requests.RequestException as e:
            logger.error(f"Network error getting user info: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service temporarily unavailable"
            )
    
    def verify_id_token(self, id_token_str: str) -> Dict[str, Any]:
        """
        Verify Google ID token (alternative method for client-side auth)
        
        Args:
            id_token_str: ID token from Google
            
        Returns:
            Verified token payload
        """
        try:
            # Verify the token with Google's library
            id_info = id_token.verify_oauth2_token(
                id_token_str, 
                google_requests.Request(), 
                self.client_id
            )
            
            # Verify the issuer
            if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Invalid issuer')
            
            logger.info(f"Verified ID token for user: {id_info.get('email')}")
            return id_info
            
        except ValueError as e:
            logger.error(f"ID token verification failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid ID token"
            )

class SessionManager:
    """Manage user sessions with expiry"""
    
    # In-memory session storage (in production, use Redis or database)
    _sessions: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def create_session(cls, user_data: Dict[str, Any]) -> str:
        """
        Create a new session for the user
        
        Args:
            user_data: User data from Google
            
        Returns:
            Session token
        """
        session_token = str(uuid.uuid4())
        
        # Store session data with expiry (7 days)
        expiry = datetime.utcnow() + timedelta(days=7)
        
        cls._sessions[session_token] = {
            'user_id': user_data.get('id'),
            'email': user_data.get('email'),
            'name': user_data.get('name'),
            'picture': user_data.get('picture'),
            'created_at': datetime.utcnow(),
            'expires_at': expiry,
            'is_active': True
        }
        
        logger.info(f"Created session for user {user_data.get('email')}")
        return session_token
    
    @classmethod
    def get_session(cls, session_token: str) -> Optional[Dict[str, Any]]:
        """
        Get session data if valid and not expired
        
        Args:
            session_token: The session token
            
        Returns:
            Session data or None if invalid/expired
        """
        session_data = cls._sessions.get(session_token)
        
        if not session_data:
            return None
        
        # Check if session is expired
        if datetime.utcnow() > session_data['expires_at']:
            cls.delete_session(session_token)
            return None
        
        # Check if session is active
        if not session_data.get('is_active', True):
            return None
        
        return session_data
    
    @classmethod
    def delete_session(cls, session_token: str) -> bool:
        """
        Delete a session
        
        Args:
            session_token: The session token to delete
            
        Returns:
            True if session was deleted, False if not found
        """
        if session_token in cls._sessions:
            del cls._sessions[session_token]
            logger.info(f"Deleted session {session_token}")
            return True
        return False
    
    @classmethod
    def extend_session(cls, session_token: str) -> bool:
        """
        Extend session expiry by 7 days
        
        Args:
            session_token: The session token to extend
            
        Returns:
            True if extended, False if session not found
        """
        session_data = cls._sessions.get(session_token)
        if session_data:
            session_data['expires_at'] = datetime.utcnow() + timedelta(days=7)
            return True
        return False

# Pydantic models for requests/responses
class GoogleAuthInitiateResponse(BaseModel):
    """Response with Google auth URL"""
    auth_url: str
    state: str

class GoogleAuthCallbackRequest(BaseModel):
    """Request from Google OAuth callback"""
    code: str
    state: Optional[str] = None

class GoogleAuthTokenRequest(BaseModel):
    """Request with Google ID token (for client-side auth)"""
    id_token: str

class AuthTokenResponse(BaseModel):
    """Response with auth token and user data"""
    access_token: str
    user: Dict[str, Any]
    expires_in: int = 604800  # 7 days in seconds

class UserProfileResponse(BaseModel):
    """User profile response"""
    id: str
    email: str
    name: str
    picture: Optional[str] = None
    created_at: datetime