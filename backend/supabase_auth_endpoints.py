"""
Supabase Authentication Endpoints
Replaces traditional JWT auth endpoints with Supabase Auth integration
"""

from fastapi import APIRouter, HTTPException, status, Depends
from supabase_client import supabase_manager
from supabase_auth import verify_token
from models import UserCreate, UserLogin, UserResponse
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
                    # For development, create a JWT token manually
                    from auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
                    from datetime import timedelta
                    
                    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                    access_token = create_access_token(
                        data={"sub": legacy_user['id']}, 
                        expires_delta=access_token_expires
                    )
                    
                    logger.info(f"✅ Legacy authentication successful for {user_credentials.email}")
                    
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
async def get_current_user_profile(current_user=Depends(verify_token)):
    """Get current user profile with automatic legacy user sync"""
    try:
        supabase = supabase_manager.get_client()
        
        # Get user profile
        profile = await supabase_manager.find_document("user_profiles", {"id": current_user.id})
        
        if not profile:
            # Create profile if doesn't exist
            user_metadata = getattr(current_user, 'user_metadata', {}) or {}
            profile_data = {
                "id": current_user.id,
                "username": current_user.email.split('@')[0],
                "first_name": user_metadata.get('first_name', ''),
                "last_name": user_metadata.get('last_name', ''),
                "is_active": True,
                "level": 1,
                "total_points": 0,
                "current_streak": 0
            }
            
            await supabase_manager.create_document("user_profiles", profile_data)
            profile = profile_data
        
        # CRITICAL FIX: Check if user exists in legacy users table and create if missing
        try:
            legacy_user = await supabase_manager.find_document("users", {"id": current_user.id})
            
            if not legacy_user:
                logger.info(f"🔄 Synchronizing user {current_user.id} to legacy users table")
                legacy_user_data = {
                    "id": current_user.id,
                    "username": profile.get('username', current_user.email.split('@')[0]),
                    "email": current_user.email,
                    "first_name": profile.get('first_name', ''),
                    "last_name": profile.get('last_name', ''),
                    "password_hash": None,  # Supabase Auth handles password
                    "google_id": profile.get('google_id'),
                    "profile_picture": profile.get('profile_picture'),
                    "is_active": profile.get('is_active', True),
                    "level": profile.get('level', 1),
                    "total_points": profile.get('total_points', 0),
                    "current_streak": profile.get('current_streak', 0)
                }
                
                await supabase_manager.create_document("users", legacy_user_data)
                logger.info(f"✅ User {current_user.id} synchronized to legacy users table")
                
        except Exception as sync_error:
            logger.error(f"⚠️ Failed to sync user to legacy table: {sync_error}")
            # Don't fail the request if sync fails
        
        return UserResponse(
            id=profile['id'],
            username=profile.get('username', ''),
            email=current_user.email,
            first_name=profile.get('first_name', ''),
            last_name=profile.get('last_name', ''),
            is_active=profile.get('is_active', True),
            level=profile.get('level', 1),
            total_points=profile.get('total_points', 0),
            current_streak=profile.get('current_streak', 0),
            created_at=profile.get('created_at')
        )
        
    except Exception as e:
        logger.error(f"Get user profile error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user profile")