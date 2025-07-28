"""
Supabase Authentication Endpoints
Replaces traditional JWT auth endpoints with Supabase Auth integration
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from supabase_client import supabase_manager
from supabase_auth import verify_token
from models import UserCreate, UserLogin, UserResponse
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Create router for auth endpoints with /auth prefix
auth_router = APIRouter(prefix="/auth")

@auth_router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    """Register a new user with Supabase Auth and ensure backward compatibility"""
    try:
        supabase = supabase_manager.get_client()
        
        # Create user in Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
            "options": {
                "data": {
                    "first_name": user_data.first_name,
                    "last_name": user_data.last_name,
                    "username": user_data.username
                }
            }
        })
        
        if auth_response.user:
            user_id = auth_response.user.id
            
            # Create user profile in our user_profiles table
            profile_data = {
                "id": user_id,
                "username": user_data.username,
                "first_name": user_data.first_name,
                "last_name": user_data.last_name,
                "is_active": True,
                "level": 1,
                "total_points": 0,
                "current_streak": 0
            }
            
            # Insert profile
            await supabase_manager.create_document("user_profiles", profile_data)
            
            # CRITICAL FIX: Also create user in legacy users table for backward compatibility
            legacy_user_data = {
                "id": user_id,  # Use same ID as Supabase Auth
                "username": user_data.username,
                "email": user_data.email,
                "first_name": user_data.first_name,
                "last_name": user_data.last_name,
                "password_hash": None,  # Supabase Auth handles password
                "google_id": None,
                "profile_picture": None,
                "is_active": True,
                "level": 1,
                "total_points": 0,
                "current_streak": 0
            }
            
            try:
                await supabase_manager.create_document("users", legacy_user_data)
                logger.info(f"✅ User {user_id} synchronized to legacy users table")
            except Exception as legacy_error:
                logger.error(f"⚠️ Failed to create legacy user record: {legacy_error}")
                # Don't fail registration if legacy table insert fails
            
            # Create initial user stats
            try:
                stats_data = {
                    "user_id": user_id,
                    "total_journal_entries": 0,
                    "total_tasks": 0,
                    "tasks_completed": 0,
                    "total_areas": 0,
                    "total_projects": 0,
                    "completed_projects": 0,
                    "courses_enrolled": 0,
                    "courses_completed": 0,
                    "badges_earned": 0
                }
                await supabase_manager.create_document("user_stats", stats_data)
                logger.info(f"✅ User stats created for {user_id}")
            except Exception as stats_error:
                logger.error(f"⚠️ Failed to create user stats: {stats_error}")
            
            return UserResponse(
                id=user_id,
                username=user_data.username,
                email=user_data.email,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                is_active=True,
                level=1,
                total_points=0,
                current_streak=0,
                created_at=auth_response.user.created_at
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Registration failed"
            )
            
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=400, detail="Registration failed")

async def get_supabase_auth_user_id(email: str) -> Optional[str]:
    """Get Supabase Auth user ID by email"""
    try:
        from supabase_client import supabase_manager
        supabase = supabase_manager.get_client()
        
        # List all auth users and find by email
        auth_users = supabase.auth.admin.list_users()
        for user in auth_users:
            if hasattr(user, 'email') and user.email == email:
                logger.info(f"Found Supabase Auth user ID for {email}: {user.id}")
                return user.id
        
        logger.warning(f"No Supabase Auth user found for email: {email}")
        return None
        
    except Exception as e:
        logger.error(f"Error getting Supabase Auth user ID: {e}")
        return None

@auth_router.post("/login")
async def login_user(user_credentials: UserLogin):
    """Login user - hybrid approach for development"""
    try:
        supabase = supabase_manager.get_client()
        
        # First, try Supabase Auth (for confirmed users)
        try:
            auth_response = supabase.auth.sign_in_with_password({
                "email": user_credentials.email,
                "password": user_credentials.password
            })
            
            if auth_response.session:
                return {
                    "access_token": auth_response.session.access_token,
                    "refresh_token": auth_response.session.refresh_token,
                    "token_type": "bearer",
                    "expires_in": auth_response.session.expires_in
                }
        except Exception as supabase_error:
            logger.info(f"Supabase auth failed: {supabase_error}")
            
            # If Supabase auth fails, try legacy auth for development
            if "Email not confirmed" in str(supabase_error) or "Invalid login credentials" in str(supabase_error):
                logger.info("Attempting legacy authentication for development...")
                
                # Check if user exists in legacy users table
                legacy_user = await supabase_manager.find_document("users", {"email": user_credentials.email})
                
                if legacy_user:
                    # Get Supabase Auth user ID for this email
                    auth_user_id = await get_supabase_auth_user_id(user_credentials.email)
                    
                    if auth_user_id:
                        # Use Supabase Auth user ID for token
                        from auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
                        from datetime import timedelta
                        
                        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                        access_token = create_access_token(
                            data={"sub": auth_user_id},  # Use auth user ID instead of legacy ID
                            expires_delta=access_token_expires
                        )
                        
                        logger.info(f"✅ Hybrid authentication successful for {user_credentials.email} with auth ID: {auth_user_id}")
                        
                        return {
                            "access_token": access_token,
                            "token_type": "bearer"
                        }
                    else:
                        # Fallback to legacy user ID if auth user not found
                        from auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
                        from datetime import timedelta
                        
                        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                        access_token = create_access_token(
                            data={"sub": legacy_user['id']}, 
                            expires_delta=access_token_expires
                        )
                        
                        logger.warning(f"⚠️ Using legacy user ID for {user_credentials.email} - auth user not found")
                        
                        return {
                            "access_token": access_token,
                            "token_type": "bearer"
                        }
        
        # If both methods fail
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_profile(request: Request):
    """Get current user profile with hybrid token verification"""
    try:
        # Get authorization header
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="No authorization token provided")
        
        token = authorization.split(" ")[1]
        current_user = None
        
        # Try Supabase token verification first
        try:
            from supabase_auth import verify_token
            current_user = await verify_token(token)
            logger.info("✅ Verified Supabase token")
        except Exception as supabase_error:
            logger.info(f"Supabase token verification failed: {supabase_error}")
            
            # Try legacy JWT token verification
            try:
                from auth import jwt, SECRET_KEY, ALGORITHM
                from models import TokenData
                
                # Decode JWT token directly
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                user_id: str = payload.get("sub")
                if user_id is None:
                    raise HTTPException(status_code=401, detail="Could not validate credentials")
                
                current_user = user_id  # For legacy tokens, current_user is just the user_id
                logger.info("✅ Verified legacy JWT token")
            except Exception as legacy_error:
                logger.info(f"Legacy token verification failed: {legacy_error}")
                raise HTTPException(status_code=401, detail="Could not validate credentials")
        
        if not current_user:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        
        # Get user data based on verification method
        supabase = supabase_manager.get_client()
        
        # Check if we have user_id or need to extract from current_user
        user_id = getattr(current_user, 'id', current_user) if hasattr(current_user, 'id') else current_user
        if isinstance(current_user, dict):
            user_id = current_user.get('id', current_user.get('sub'))
        
        logger.info(f"Looking up user: {user_id}")
        
        # First try to get user from legacy users table
        try:
            legacy_user = await supabase_manager.find_document("users", {"id": user_id})
            
            if legacy_user:
                logger.info("✅ Found user in legacy users table")
                return UserResponse(
                    id=legacy_user['id'],
                    username=legacy_user.get('username', ''),
                    email=legacy_user.get('email', ''),
                    first_name=legacy_user.get('first_name', ''),
                    last_name=legacy_user.get('last_name', ''),
                    is_active=legacy_user.get('is_active', True),
                    level=legacy_user.get('level', 1),
                    total_points=legacy_user.get('total_points', 0),
                    current_streak=legacy_user.get('current_streak', 0),
                    created_at=legacy_user.get('created_at')
                )
        except Exception as legacy_lookup_error:
            logger.info(f"Legacy user lookup failed: {legacy_lookup_error}")
        
        # Fallback to user_profiles table
        try:
            profile = await supabase_manager.find_document("user_profiles", {"id": user_id})
            
            if profile:
                logger.info("✅ Found user in user_profiles table")
                return UserResponse(
                    id=profile['id'],
                    username=profile.get('username', ''),
                    email=getattr(current_user, 'email', ''),
                    first_name=profile.get('first_name', ''),
                    last_name=profile.get('last_name', ''),
                    is_active=profile.get('is_active', True),
                    level=profile.get('level', 1),
                    total_points=profile.get('total_points', 0),
                    current_streak=profile.get('current_streak', 0),
                    created_at=profile.get('created_at')
                )
        except Exception as profile_lookup_error:
            logger.info(f"Profile lookup failed: {profile_lookup_error}")
        
        # If no user found, return error
        raise HTTPException(status_code=404, detail="User not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user profile error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user profile")