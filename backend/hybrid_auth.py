"""
Hybrid Authentication Module
Supports both Supabase and legacy JWT tokens for backward compatibility
"""

from fastapi import HTTPException, status, Depends, Request
from models import User
import logging

logger = logging.getLogger(__name__)

async def get_current_user_hybrid(request: Request) -> User:
    """Get current user with hybrid token verification (Supabase + Legacy JWT)"""
    try:
        # Get authorization header
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="No authorization token provided")
        
        token = authorization.split(" ")[1]
        current_user = None
        user_id = None
        
        # Try Supabase token verification first
        try:
            from supabase_auth import SupabaseAuth
            from fastapi.security import HTTPAuthorizationCredentials
            
            # Create credentials object for Supabase auth
            credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
            supabase_user = await SupabaseAuth.verify_token(credentials)
            current_user = await SupabaseAuth.get_current_user(supabase_user)
            logger.info("✅ Verified Supabase token for API endpoint")
            return current_user
            
        except Exception as supabase_error:
            logger.info(f"Supabase token verification failed: {supabase_error}")
            
            # Try legacy JWT token verification
            try:
                from auth import jwt, SECRET_KEY, ALGORITHM
                from supabase_client import supabase_manager
                
                # Decode JWT token directly
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                user_id = payload.get("sub")
                if user_id is None:
                    raise HTTPException(status_code=401, detail="Could not validate credentials")
                
                logger.info("✅ Verified legacy JWT token for API endpoint")
                
                # Get user data from database
                # First try user_profiles table (which uses auth user IDs)
                try:
                    user_profile = await supabase_manager.find_document("user_profiles", {"id": user_id})
                    
                    if user_profile:
                        logger.info("✅ Found user in user_profiles table")
                        return User(
                            id=user_profile['id'],
                            username=user_profile.get('username', ''),
                            email='',  # We'll need to get this from auth or legacy table
                            first_name=user_profile.get('first_name', ''),
                            last_name=user_profile.get('last_name', ''),
                            is_active=user_profile.get('is_active', True),
                            level=user_profile.get('level', 1),
                            total_points=user_profile.get('total_points', 0),
                            current_streak=user_profile.get('current_streak', 0),
                            created_at=user_profile.get('created_at', '2025-01-01T00:00:00'),
                            updated_at=user_profile.get('updated_at', '2025-01-01T00:00:00')
                        )
                except Exception as e:
                    logger.info(f"User_profiles lookup failed: {e}")
                
                # Fallback: try to get user from legacy users table  
                try:
                    legacy_user = await supabase_manager.find_document("users", {"id": user_id})
                    
                    if legacy_user:
                        logger.info("✅ Found user in legacy users table")
                        return User(
                            id=legacy_user['id'],
                            username=legacy_user.get('username', ''),
                            email=legacy_user.get('email', ''),
                            first_name=legacy_user.get('first_name', ''),
                            last_name=legacy_user.get('last_name', ''),
                            is_active=legacy_user.get('is_active', True),
                            level=legacy_user.get('level', 1),
                            total_points=legacy_user.get('total_points', 0),
                            current_streak=legacy_user.get('current_streak', 0),
                            created_at=legacy_user.get('created_at'),
                            updated_at=legacy_user.get('updated_at')
                        )
                except Exception as legacy_lookup_error:
                    logger.info(f"Legacy user lookup failed: {legacy_lookup_error}")
                
                # If no user found yet, attempt to create a minimal user_profiles record using Supabase Auth email
                try:
                    from supabase_client import supabase_manager
                    supabase = supabase_manager.get_client()

                    # Try to discover auth user email via admin API
                    try:
                        auth_users = supabase.auth.admin.list_users()
                        auth_email = None
                        for au in auth_users:
                            if hasattr(au, 'id') and au.id == user_id:
                                auth_email = getattr(au, 'email', None)
                                break
                    except Exception as _:
                        auth_email = None

                    # Create a minimal profile tied to the Supabase Auth ID so other endpoints work
                    profile_data = {
                        'id': user_id,
                        'username': (auth_email.split('@')[0] if isinstance(auth_email, str) and '@' in auth_email else 'user'),
                        'first_name': '',
                        'last_name': '',
                        'is_active': True,
                        'level': 1,
                        'total_points': 0,
                        'current_streak': 0
                    }

                    try:
                        supabase.table('user_profiles').insert(profile_data).execute()
                        logger.info("✅ Created minimal user_profiles record for auth user")
                        return User(
                            id=profile_data['id'],
                            username=profile_data['username'],
                            email=auth_email or '',
                            first_name=profile_data['first_name'],
                            last_name=profile_data['last_name'],
                            is_active=True,
                            level=1,
                            total_points=0,
                            current_streak=0,
                            created_at=profile_data.get('created_at', '2025-01-01T00:00:00'),
                            updated_at=profile_data.get('updated_at', '2025-01-01T00:00:00')
                        )
                    except Exception as create_err:
                        logger.info(f"Failed to create minimal user profile: {create_err}")

                except Exception as e2:
                    logger.info(f"Profile bootstrap attempt failed: {e2}")

                # If still no user found, return error
                raise HTTPException(status_code=404, detail="User not found")
                
            except Exception as legacy_error:
                logger.info(f"Legacy token verification failed: {legacy_error}")
                raise HTTPException(status_code=401, detail="Could not validate credentials")
        
        # If both methods fail
        raise HTTPException(status_code=401, detail="Could not validate credentials")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Hybrid auth error: {e}")
        raise HTTPException(status_code=500, detail="Authentication error")

async def get_current_active_user_hybrid(current_user: User = Depends(get_current_user_hybrid)) -> User:
    """Get current active user with hybrid authentication"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user