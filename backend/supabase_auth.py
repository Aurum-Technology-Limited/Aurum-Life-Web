"""
Supabase Authentication Module
Replaces custom JWT auth with Supabase Auth
"""

import os
from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from models import User
import logging

logger = logging.getLogger(__name__)

# Load Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# HTTP Bearer for token authentication
security = HTTPBearer()

class SupabaseAuth:
    """Supabase authentication handler"""
    
    @staticmethod
    async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
        """Verify Supabase JWT token and return user data.
        Note: Allows manual invocation with a raw token string for compatibility.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            # Support both FastAPI-injected credentials and direct string token usage
            if isinstance(credentials, str):
                token = credentials
            elif hasattr(credentials, 'credentials'):
                token = credentials.credentials
            else:
                raise credentials_exception
            
            # Verify token with Supabase
            user_response = supabase.auth.get_user(token)
            
            if not getattr(user_response, 'user', None):
                raise credentials_exception
            
            return user_response.user
            
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            raise credentials_exception
    
    @staticmethod
    async def get_current_user(supabase_user: dict) -> User:
        """Get current authenticated user with profile data"""
        try:
            # Get user profile from our user_profiles table
            profile_response = supabase.table('user_profiles').select('*').eq('id', supabase_user.id).single().execute()
            
            if not profile_response.data:
                # If no profile exists, create a basic one from Supabase user data
                user_metadata = supabase_user.user_metadata or {}
                profile_data = {
                    'id': supabase_user.id,
                    'username': supabase_user.email.split('@')[0],  # Generate username from email
                    'first_name': user_metadata.get('first_name', ''),
                    'last_name': user_metadata.get('last_name', ''),
                    'is_active': True,
                    'level': 1,
                    'total_points': 0,
                    'current_streak': 0
                }
                
                # Create the profile
                supabase.table('user_profiles').insert(profile_data).execute()
                profile_response.data = profile_data
            
            # Convert to User model
            profile = profile_response.data
            user = User(
                id=profile['id'],
                email=supabase_user.email,
                username=profile.get('username', ''),
                first_name=profile.get('first_name', ''),
                last_name=profile.get('last_name', ''),
                google_id=profile.get('google_id'),
                profile_picture=profile.get('profile_picture'),
                is_active=profile.get('is_active', True),
                level=profile.get('level', 1),
                total_points=profile.get('total_points', 0),
                current_streak=profile.get('current_streak', 0),
                created_at=profile.get('created_at'),
                updated_at=profile.get('updated_at')
            )
            
            return user
            
        except Exception as e:
            logger.error(f"Failed to get current user: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

# Export functions for use in FastAPI dependencies
async def get_current_user(supabase_user: dict = Depends(SupabaseAuth.verify_token)) -> User:
    """Get current authenticated user with profile data"""
    return await SupabaseAuth.get_current_user(supabase_user)

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

# Export token verification function
verify_token = SupabaseAuth.verify_token
