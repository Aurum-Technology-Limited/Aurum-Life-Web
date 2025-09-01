"""
@fileoverview Supabase Authentication Endpoints

Provides secure authentication endpoints using Supabase Auth integration.
Handles user registration, login, password reset, and token management
with comprehensive error handling and security measures.

@version 1.0.0
@author Aurum Life Development Team
"""

import os
import re
import urllib.parse
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, status, Request, Depends
from pydantic import BaseModel, EmailStr, validator

from supabase_client import supabase_manager
from supabase_auth import verify_token, get_current_active_user
from models import UserCreate, UserLogin, UserResponse, User

# Configure logging
logger = logging.getLogger(__name__)

# Configuration constants
AUTH_CONFIG = {
    'PASSWORD_RESET_TIMEOUT': 3600,  # 1 hour
    'REQUEST_TIMEOUT': 30,  # seconds
    'MAX_RETRY_ATTEMPTS': 3,
    'PREVIEW_DOMAIN': 'https://aurum-codebase.preview.emergentagent.com'
}

# Create router
auth_router = APIRouter(prefix="/auth", tags=["authentication"])


class RefreshRequest(BaseModel):
    """Request model for token refresh"""
    refresh_token: str
    
    @validator('refresh_token')
    def validate_refresh_token(cls, v):
        if not v or not v.strip():
            raise ValueError('Refresh token cannot be empty')
        return v.strip()


class ForgotPasswordRequest(BaseModel):
    """Request model for forgot password"""
    email: EmailStr
    
    @validator('email')
    def validate_email(cls, v):
        return v.lower().strip()


class UpdatePasswordRequest(BaseModel):
    """Request model for password update"""
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        return v


class SupabaseError(Exception):
    """Custom exception for Supabase-related errors"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class UserManager:
    """Handles user-related operations with Supabase"""
    
    @staticmethod
    async def check_existing_user(email: str) -> bool:
        """
        Checks if user already exists in Supabase
        
        Args:
            email (str): User email to check
            
        Returns:
            bool: True if user exists, False otherwise
        """
        try:
            supabase = supabase_manager.get_client()
            existing = supabase.auth.admin.list_users()
            existing_users = (
                existing.users if hasattr(existing, 'users') 
                else existing.get('users') if isinstance(existing, dict) 
                else existing
            )
            
            for user in (existing_users or []):
                user_email = (
                    getattr(user, 'email', None) if hasattr(user, 'email')
                    else user.get('email') if isinstance(user, dict)
                    else None
                )
                
                if isinstance(user_email, str) and user_email.lower() == email.lower():
                    return True
                    
            return False
            
        except Exception as e:
            logger.warning(f"Could not check existing users: {e}")
            return False
    
    @staticmethod
    async def create_user_profile(user_id: str, user_data: UserCreate) -> None:
        """
        Creates user profile in database
        
        Args:
            user_id (str): Supabase user ID
            user_data (UserCreate): User registration data
        """
        profile_data = {
            "id": user_id,
            "username": user_data.username or user_data.email.split('@')[0],
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "birth_date": user_data.birth_date.isoformat() if user_data.birth_date else None,
            "is_active": True,
            "level": 1,
            "total_points": 0,
            "current_streak": 0
        }
        
        await supabase_manager.create_document("user_profiles", profile_data)
    
    @staticmethod
    def extract_user_info(auth_response) -> tuple:
        """
        Extracts user information from Supabase auth response
        
        Args:
            auth_response: Supabase auth response
            
        Returns:
            tuple: (user_id, created_at)
        """
        supa_user = (
            getattr(auth_response, 'user', None) or 
            getattr(auth_response, 'data', None) or 
            auth_response
        )
        
        user_id = (
            getattr(supa_user, 'id', None) or 
            (supa_user.get('id') if isinstance(supa_user, dict) else None)
        )
        
        created_at = (
            getattr(supa_user, 'created_at', None) or 
            (supa_user.get('created_at') if isinstance(supa_user, dict) else None)
        )
        
        return user_id, created_at


class URLBuilder:
    """Handles URL construction for password reset flows"""
    
    @staticmethod
    def extract_origin_from_request(request: Request) -> str:
        """
        Extracts origin URL from request with fallbacks
        
        Args:
            request (Request): FastAPI request object
            
        Returns:
            str: Origin URL
        """
        # Try origin header first
        origin = request.headers.get('origin')
        
        if not origin:
            # Construct from scheme and host
            scheme = request.url.scheme
            host = request.headers.get('host')
            if scheme and host:
                origin = f"{scheme}://{host}"
        
        # Handle localhost/development environments
        if origin and ("localhost" in origin or "127.0.0.1" in origin):
            origin = AUTH_CONFIG['PREVIEW_DOMAIN']
        elif not origin:
            origin = AUTH_CONFIG['PREVIEW_DOMAIN']
        
        return origin
    
    @staticmethod
    def build_redirect_url(origin: str) -> str:
        """
        Builds password reset redirect URL
        
        Args:
            origin (str): Base origin URL
            
        Returns:
            str: Complete redirect URL
        """
        return f"{origin}/reset-password" if origin else None


class PasswordResetService:
    """Handles password reset operations"""
    
    @staticmethod
    async def send_reset_email(email: str, redirect_url: str) -> Dict[str, Any]:
        """
        Sends password reset email via Supabase
        
        Args:
            email (str): User email
            redirect_url (str): Redirect URL for reset page
            
        Returns:
            dict: Operation result
        """
        try:
            supabase = supabase_manager.get_client()
            
            # Use standard reset method with proper redirect
            if redirect_url:
                supabase.auth.reset_password_for_email(
                    email,
                    {"redirectTo": redirect_url}
                )
            else:
                supabase.auth.reset_password_for_email(email)
            
            logger.info(f"Password reset email sent successfully for: {email}")
            
            return {
                "success": True,
                "message": "If an account exists, a password reset email has been sent."
            }
            
        except Exception as e:
            logger.error(f"Password reset email failed for {email}: {e}")
            # Always return success to prevent email enumeration
            return {
                "success": True,
                "message": "If an account exists, a password reset email has been sent."
            }
    
    @staticmethod
    async def update_password_with_token(token: str, new_password: str) -> Dict[str, Any]:
        """
        Updates user password using recovery token
        
        Args:
            token (str): Recovery token
            new_password (str): New password
            
        Returns:
            dict: Update result
        """
        try:
            supabase = supabase_manager.get_client()
            
            # Method 1: Try setting session and updating password
            try:
                session_response = supabase.auth.set_session(access_token=token, refresh_token=None)
                logger.info("Session set successfully with recovery token")
                
                result = supabase.auth.update_user({"password": new_password})
                logger.info("Password updated successfully via session method")
                
                return {"success": True, "message": "Password updated successfully"}
                
            except Exception as session_error:
                logger.warning(f"Session method failed: {session_error}")
                
                # Method 2: Try admin API as fallback
                try:
                    user_response = supabase.auth.get_user(token)
                    user = user_response.user if hasattr(user_response, 'user') else user_response
                    user_id = getattr(user, 'id', None)
                    
                    if user_id:
                        admin_result = supabase.auth.admin.update_user_by_id(
                            user_id,
                            {"password": new_password}
                        )
                        logger.info("Password updated successfully via admin API")
                        
                        return {"success": True, "message": "Password updated successfully"}
                    else:
                        raise Exception("Could not extract user ID from token")
                        
                except Exception as admin_error:
                    logger.error(f"Admin method failed: {admin_error}")
                    raise Exception("All password update methods failed")
            
        except Exception as e:
            logger.error(f"Password update failed completely: {e}")
            raise SupabaseError("Failed to update password. Token may have expired.", 400)


# API Endpoints

@auth_router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    """
    Register a new user with Supabase Auth
    
    Args:
        user_data (UserCreate): User registration data
        
    Returns:
        UserResponse: Created user information
        
    Raises:
        HTTPException: If registration fails or user already exists
    """
    try:
        # Check for existing user
        if await UserManager.check_existing_user(user_data.email):
            raise HTTPException(
                status_code=409, 
                detail="Email already registered. Please log in instead."
            )
        
        # Create user in Supabase Auth
        supabase = supabase_manager.get_client()
        admin_payload = {
            "email": user_data.email,
            "password": user_data.password,
            "email_confirm": True,
            "user_metadata": {
                "first_name": user_data.first_name,
                "last_name": user_data.last_name,
                "username": user_data.username
            }
        }
        
        auth_response = supabase.auth.admin.create_user(admin_payload)
        user_id, created_at = UserManager.extract_user_info(auth_response)
        
        if not user_id:
            raise SupabaseError("Failed to create user in Supabase")
        
        # Create user profile
        await UserManager.create_user_profile(user_id, user_data)
        
        # Return user response
        return UserResponse(
            id=user_id,
            username=user_data.username or user_data.email.split('@')[0],
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            is_active=True,
            has_completed_onboarding=False,
            created_at=created_at or "2025-01-01T00:00:00"
        )
        
    except HTTPException:
        raise
    except SupabaseError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Registration error: {e}")
        error_msg = str(e).lower()
        
        if "already" in error_msg and "register" in error_msg:
            raise HTTPException(
                status_code=409, 
                detail="Email already registered. Please log in instead."
            )
        
        raise HTTPException(
            status_code=400, 
            detail=f"Registration failed: {str(e)}"
        )


@auth_router.post("/login")
async def login_user(user_credentials: UserLogin):
    """
    Authenticate user with Supabase Auth
    
    Args:
        user_credentials (UserLogin): Login credentials
        
    Returns:
        dict: Authentication tokens and metadata
        
    Raises:
        HTTPException: If login fails
    """
    try:
        supabase = supabase_manager.get_client()
        
        auth_response = supabase.auth.sign_in_with_password({
            "email": user_credentials.email,
            "password": user_credentials.password
        })
        
        # Validate response and extract session
        if (hasattr(auth_response, 'session') and 
            auth_response.session and 
            hasattr(auth_response.session, 'access_token')):
            
            session = auth_response.session
            
            return {
                "access_token": session.access_token,
                "refresh_token": getattr(session, 'refresh_token', None),
                "token_type": "bearer",
                "expires_in": getattr(session, 'expires_in', 3600)
            }
        
        raise SupabaseError("Invalid credentials", 401)
        
    except HTTPException:
        raise
    except SupabaseError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=401, detail="Invalid credentials")


@auth_router.post("/refresh")
async def refresh_session(payload: RefreshRequest):
    """
    Refresh authentication session
    
    Args:
        payload (RefreshRequest): Refresh token request
        
    Returns:
        dict: New authentication tokens
        
    Raises:
        HTTPException: If refresh fails
    """
    try:
        supabase = supabase_manager.get_client()
        
        # Try primary refresh method
        try:
            refreshed = supabase.auth.refresh_session({
                "refresh_token": payload.refresh_token
            })
        except Exception as e:
            logger.info(f"Primary refresh method failed: {e}")
            
            # Try fallback method
            try:
                refreshed = supabase.auth.set_session({
                    "refresh_token": payload.refresh_token, 
                    "access_token": ""
                })
            except Exception as e2:
                logger.error(f"Fallback refresh failed: {e2}")
                raise SupabaseError("Failed to refresh session", 401)
        
        # Extract session data
        session = (
            getattr(refreshed, 'session', None) or 
            getattr(refreshed, 'data', None) or 
            refreshed
        )
        
        if not session:
            raise SupabaseError("No session data in refresh response", 401)
        
        access_token = getattr(session, 'access_token', None)
        if not access_token:
            raise SupabaseError("No access token in refresh response", 401)
        
        return {
            "access_token": access_token,
            "refresh_token": getattr(session, 'refresh_token', None) or payload.refresh_token,
            "token_type": "bearer",
            "expires_in": getattr(session, 'expires_in', 3600)
        }
        
    except HTTPException:
        raise
    except SupabaseError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Refresh session error: {e}")
        raise HTTPException(status_code=401, detail="Failed to refresh session")


@auth_router.post("/forgot-password")
async def forgot_password(payload: ForgotPasswordRequest, request: Request):
    """
    Trigger password reset email
    
    Args:
        payload (ForgotPasswordRequest): Email for password reset
        request (Request): FastAPI request object
        
    Returns:
        dict: Success response (always returns success for security)
    """
    try:
        # Build redirect URL
        origin = URLBuilder.extract_origin_from_request(request)
        redirect_url = URLBuilder.build_redirect_url(origin)
        
        logger.info(f"Forgot password redirect URL: {redirect_url}")
        
        # Send reset email
        result = await PasswordResetService.send_reset_email(payload.email, redirect_url)
        return result
        
    except Exception as e:
        logger.error(f"Forgot password error: {e}")
        # Always return success to prevent email enumeration
        return {
            "success": True,
            "message": "If an account exists, a password reset email has been sent."
        }


@auth_router.post("/update-password")
async def update_password(payload: UpdatePasswordRequest, request: Request):
    """
    Update user password using recovery token
    
    Args:
        payload (UpdatePasswordRequest): New password data
        request (Request): FastAPI request object (for token extraction)
        
    Returns:
        dict: Update success response
        
    Raises:
        HTTPException: If token is invalid or password update fails
    """
    try:
        # Extract token from Authorization header
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=401, 
                detail="No authorization token provided"
            )
        
        token = authorization.split(" ")[1]
        logger.info("Attempting password update with recovery token")
        
        # Update password
        result = await PasswordResetService.update_password_with_token(
            token, 
            payload.new_password
        )
        
        return result
        
    except HTTPException:
        raise
    except SupabaseError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Update password error: {e}")
        raise HTTPException(status_code=400, detail="Failed to update password")


@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_profile(request: Request):
    """
    Get current user profile information
    
    Args:
        request (Request): FastAPI request object
        
    Returns:
        UserResponse: Current user profile data
        
    Raises:
        HTTPException: If authentication fails or user not found
    """
    try:
        # Extract and verify token
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=401, 
                detail="No authorization token provided"
            )
        
        token = authorization.split(" ")[1]
        current_user = await verify_token(token)
        
        # Extract user ID
        user_id = (
            getattr(current_user, 'id', None) or 
            (current_user.get('id') if isinstance(current_user, dict) else None)
        )
        
        if not user_id:
            raise HTTPException(
                status_code=401, 
                detail="Could not validate credentials"
            )
        
        # Fetch or create user profile
        profile = await supabase_manager.find_document("user_profiles", {"id": user_id})
        
        if not profile:
            # Create default profile for new users
            username = (
                current_user.email.split('@')[0] 
                if hasattr(current_user, 'email') 
                else 'user'
            )
            
            default_profile = {
                'id': user_id,
                'username': username,
                'first_name': '',
                'last_name': '',
                'is_active': True,
                'level': 1,
                'total_points': 0,
                'current_streak': 0
            }
            
            await supabase_manager.create_document("user_profiles", default_profile)
            profile = await supabase_manager.find_document("user_profiles", {"id": user_id})
        
        # Determine onboarding status
        has_completed_onboarding = (profile.get('level', 1) >= 2)
        
        # Build user response
        return UserResponse(
            id=profile['id'],
            username=profile.get('username', ''),
            email=(
                current_user.email if hasattr(current_user, 'email') 
                else profile.get('email', '')
            ),
            first_name=profile.get('first_name', ''),
            last_name=profile.get('last_name', ''),
            is_active=profile.get('is_active', True),
            has_completed_onboarding=has_completed_onboarding,
            created_at=profile.get('created_at', '2025-01-01T00:00:00')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user profile error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user profile")


@auth_router.post("/complete-onboarding")
async def complete_onboarding(current_user: User = Depends(get_current_active_user)):
    """
    Mark user onboarding as complete
    
    Args:
        current_user (User): Current authenticated user
        
    Returns:
        dict: Success response
        
    Raises:
        HTTPException: If onboarding completion fails
    """
    try:
        user_id = str(current_user.id)
        
        # Find or create user profile
        profile = await supabase_manager.find_document("user_profiles", {"id": user_id})
        
        if not profile:
            # Create new profile with completed onboarding
            new_profile = {
                'id': user_id,
                'username': '',
                'first_name': '',
                'last_name': '',
                'is_active': True,
                'level': 2,  # Level 2 indicates completed onboarding
                'total_points': 0,
                'current_streak': 0
            }
            await supabase_manager.create_document("user_profiles", new_profile)
        else:
            # Update existing profile if onboarding not complete
            current_level = profile.get('level', 1)
            if current_level < 2:
                await supabase_manager.update_document(
                    "user_profiles", 
                    user_id, 
                    {"level": 2}
                )
        
        return {"success": True}
        
    except Exception as e:
        logger.error(f"Failed to complete onboarding: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to complete onboarding"
        )


@auth_router.get("/debug-supabase-config")
async def debug_supabase_config():
    """
    Debug endpoint for Supabase configuration verification
    
    Returns:
        dict: Configuration information for debugging
    """
    try:
        return {
            "supabase_url": os.getenv('SUPABASE_URL'),
            "expected_site_url": AUTH_CONFIG['PREVIEW_DOMAIN'],
            "expected_redirect_url": f"{AUTH_CONFIG['PREVIEW_DOMAIN']}/reset-password",
            "message": "Check these URLs match your Supabase Auth URL Configuration exactly"
        }
    except Exception as e:
        return {"error": str(e)}