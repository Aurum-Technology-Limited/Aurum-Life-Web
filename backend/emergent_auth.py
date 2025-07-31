"""
Emergent Authentication Service for Google OAuth Integration
"""

import os
import uuid
import aiohttp
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class EmergentAuthService:
    """Service for handling Emergent authentication"""
    
    EMERGENT_AUTH_URL = "https://auth.emergentagent.com/"
    EMERGENT_API_URL = "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data"
    
    @classmethod
    async def get_session_data(cls, session_id: str) -> Dict[str, Any]:
        """
        Get user session data from Emergent API
        
        Args:
            session_id: The session ID from the redirect
            
        Returns:
            User data dictionary with id, email, name, picture, session_token
        """
        try:
            headers = {
                "X-Session-ID": session_id,
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(cls.EMERGENT_API_URL, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Successfully retrieved session data for session {session_id}")
                        return data
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to get session data: {response.status} - {error_text}")
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid session ID or expired session"
                        )
                        
        except aiohttp.ClientError as e:
            logger.error(f"Network error getting session data: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service temporarily unavailable"
            )
        except Exception as e:
            logger.error(f"Unexpected error getting session data: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication error"
            )
    
    @classmethod
    def generate_auth_url(cls, redirect_url: str) -> str:
        """
        Generate the Emergent auth URL with redirect parameter
        
        Args:
            redirect_url: The URL to redirect to after authentication
            
        Returns:
            The complete auth URL
        """
        return f"{cls.EMERGENT_AUTH_URL}?redirect={redirect_url}"

class SessionManager:
    """Manage user sessions with expiry"""
    
    # In-memory session storage (in production, use Redis or database)
    _sessions: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def create_session(cls, user_data: Dict[str, Any]) -> str:
        """
        Create a new session for the user
        
        Args:
            user_data: User data from Emergent API
            
        Returns:
            Session token
        """
        session_token = user_data.get('session_token') or str(uuid.uuid4())
        
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
class GoogleAuthRequest(BaseModel):
    """Request to initiate Google auth"""
    redirect_url: str

class GoogleAuthResponse(BaseModel):
    """Response with auth URL"""
    auth_url: str

class SessionValidationRequest(BaseModel):
    """Request to validate session ID from redirect"""
    session_id: str

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