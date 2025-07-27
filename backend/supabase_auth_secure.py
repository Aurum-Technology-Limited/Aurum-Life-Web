"""
Secure Supabase Authentication for Aurum Life MVP v1.2
Implements robust token validation with no legacy system fallbacks
"""

import os
from typing import Optional, Dict
from datetime import datetime, timedelta
import jwt
from supabase import create_client, Client
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

if not all([SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_JWT_SECRET]):
    raise ValueError("Missing required Supabase environment variables")

# Create Supabase clients
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY) if SUPABASE_SERVICE_KEY else None

class SecureAuthService:
    """Handles all authentication operations securely"""
    
    @staticmethod
    async def verify_token(token: str) -> Dict:
        """
        Verify a Supabase JWT token
        
        Args:
            token: JWT token from Authorization header
            
        Returns:
            User data dict if valid
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            # Decode and verify JWT
            payload = jwt.decode(
                token,
                SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                audience="authenticated",
                options={"verify_exp": True}
            )
            
            # Extract user ID
            user_id = payload.get("sub")
            if not user_id:
                raise ValueError("Invalid token payload - missing user ID")
            
            # Get user details from Supabase Auth
            if supabase_admin:
                user_response = supabase_admin.auth.admin.get_user_by_id(user_id)
                if user_response and user_response.user:
                    return {
                        "id": user_response.user.id,
                        "email": user_response.user.email,
                        "email_verified": user_response.user.email_confirmed_at is not None,
                        "created_at": user_response.user.created_at,
                        "is_active": True,  # Can be enhanced with custom logic
                        "metadata": user_response.user.user_metadata
                    }
            
            # Fallback to basic payload data
            return {
                "id": user_id,
                "email": payload.get("email"),
                "email_verified": payload.get("email_verified", False),
                "is_active": True
            }
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )
    
    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[Dict]:
        """
        Get user details by ID from Supabase
        
        Args:
            user_id: Supabase user ID
            
        Returns:
            User data dict or None
        """
        try:
            if not supabase_admin:
                logger.warning("Admin client not available")
                return None
                
            response = supabase_admin.auth.admin.get_user_by_id(user_id)
            if response and response.user:
                return {
                    "id": response.user.id,
                    "email": response.user.email,
                    "created_at": response.user.created_at,
                    "last_sign_in": response.user.last_sign_in_at,
                    "metadata": response.user.user_metadata
                }
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user by ID: {str(e)}")
            return None
    
    @staticmethod
    async def refresh_token(refresh_token: str) -> Dict:
        """
        Refresh an access token using a refresh token
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New token pair (access_token, refresh_token)
            
        Raises:
            HTTPException: If refresh fails
        """
        try:
            response = supabase.auth.refresh_session(refresh_token)
            
            if response and response.session:
                return {
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                    "expires_in": 3600,  # 1 hour
                    "token_type": "bearer"
                }
            
            raise ValueError("Failed to refresh token")
            
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to refresh authentication token"
            )
    
    @staticmethod
    def validate_password_strength(password: str) -> bool:
        """
        Validate password meets security requirements
        
        Requirements:
        - At least 8 characters
        - Contains uppercase and lowercase
        - Contains at least one number
        - Contains at least one special character
        """
        if len(password) < 8:
            return False
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        return all([has_upper, has_lower, has_digit, has_special])

# Global auth service instance
auth_service = SecureAuthService()

# Convenience functions for backward compatibility
async def verify_supabase_token(token: str) -> Dict:
    """Verify a Supabase JWT token"""
    return await auth_service.verify_token(token)

async def get_current_user(token: str) -> Dict:
    """Get current user from token"""
    return await auth_service.verify_token(token)