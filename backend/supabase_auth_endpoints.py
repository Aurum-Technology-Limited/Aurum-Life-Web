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

# Create router for auth endpoints with /api/auth prefix (no prefix since it will be included in api_router)
auth_router = APIRouter(tags=["authentication"])

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
        
        # Handle specific Supabase errors
        if "email rate limit" in str(e).lower():
            raise HTTPException(
                status_code=429,
                detail="Registration rate limit exceeded. Please try again in a few minutes."
            )
        elif "email already registered" in str(e).lower() or "user already registered" in str(e).lower():
            raise HTTPException(
                status_code=409,
                detail="Email already registered. Please try logging in instead."
            )
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Registration failed: {str(e)}"
            )

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
                    # CRITICAL SECURITY FIX: Verify password for legacy users
                    if legacy_user.get('password_hash'):
                        from auth import verify_password
                        if not verify_password(user_credentials.password, legacy_user['password_hash']):
                            logger.warning(f"Invalid password for legacy user {user_credentials.email}")
                            raise HTTPException(
                                status_code=401,
                                detail="Invalid credentials"
                            )
                    
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
                        
                        logger.info(f"🔍 LOGIN TOKEN DEBUG: Created JWT with user_id: {auth_user_id} from Supabase Auth")
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
                        
                        logger.info(f"🔍 LOGIN TOKEN DEBUG: Created JWT with user_id: {legacy_user['id']} from legacy users table")
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
                logger.info(f"🔍 JWT DEBUG: Decoded payload: {payload}")
                logger.info(f"🔍 JWT DEBUG: Extracted user_id from 'sub' claim: {user_id}")
                
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
        
        logger.info(f"🔍 TOKEN DEBUG: Looking up user: {user_id}")
        logger.info(f"🔍 TOKEN DEBUG: Current user type: {type(current_user)}")
        logger.info(f"🔍 TOKEN DEBUG: Current user data: {current_user}")
        
        # CRITICAL FIX: First try to find user by auth user ID, if not found, try to find by email
        user_profile = None
        legacy_user = None
        
        # Get email from auth token first (this is the most reliable identifier)
        user_email = None
        if hasattr(current_user, 'email'):
            user_email = current_user.email
        elif isinstance(current_user, str):
            # For JWT tokens, we need to find the email associated with this user ID
            try:
                # Try to get email from Supabase Auth user
                supabase = supabase_manager.get_client()
                auth_users = supabase.auth.admin.list_users()
                for auth_user in auth_users:
                    if hasattr(auth_user, 'id') and auth_user.id == user_id:
                        user_email = auth_user.email
                        logger.info(f"🔍 EMAIL DEBUG: Found email {user_email} for auth user ID {user_id}")
                        break
            except Exception as e:
                logger.error(f"Failed to get email from auth user: {e}")
        
        # Method 1: Try to get user profile by auth user ID first
        try:
            user_profile = await supabase_manager.find_document("user_profiles", {"id": user_id})
            logger.info(f"🔍 USER_PROFILES QUERY: SELECT * FROM user_profiles WHERE id = '{user_id}'")
            
            if user_profile:
                logger.info(f"✅ Found user in user_profiles table: {user_profile.get('username')} (ID: {user_profile.get('id')})")
                
                # VALIDATION: If we have email, check if this profile matches the authenticated email
                if user_email:
                    profile_email = user_profile.get('email') or user_profile.get('username')
                    if user_email not in str(profile_email).lower():
                        logger.warning(f"🚨 USER MISMATCH DETECTED: Auth email {user_email} doesn't match profile {profile_email}")
                        user_profile = None  # Force fallback to email-based lookup
                
            else:
                logger.info(f"❌ No user found in user_profiles table for ID: {user_id}")
        except Exception as e:
            logger.error(f"User_profiles lookup failed: {e}")
        
        # Method 2: If not found by ID or mismatch detected, try to find by email
        if not user_profile and user_email:
            try:
                logger.info(f"🔍 EMAIL-BASED LOOKUP: Looking for email {user_email}")
                
                # Try legacy users table by email (user_profiles doesn't have email column)
                legacy_user = await supabase_manager.find_document("users", {"email": user_email})
                
                if legacy_user:
                    logger.info(f"✅ Found legacy user by email: {legacy_user.get('username')} (ID: {legacy_user.get('id')})")
                    
                    # Also check if there's a corresponding user_profiles record with the correct ID
                    try:
                        correct_profile = await supabase_manager.find_document("user_profiles", {"id": legacy_user['id']})
                        if correct_profile:
                            logger.info(f"✅ Found corresponding user_profiles record: {correct_profile.get('username')} (ID: {correct_profile.get('id')})")
                            user_profile = correct_profile
                        else:
                            logger.info(f"⚠️ No user_profiles record found for correct user ID: {legacy_user['id']}")
                    except Exception as profile_lookup_error:
                        logger.error(f"Failed to lookup user_profiles by correct ID: {profile_lookup_error}")
                else:
                    logger.info(f"❌ No user found by email {user_email}")
            except Exception as e:
                logger.error(f"Email-based user lookup failed: {e}")
        
        # Return user profile if found
        if user_profile:
            # Map level field to has_completed_onboarding (level 2 = completed, level 1 = not completed)
            level = user_profile.get('level', 1)
            has_completed_onboarding = level >= 2
            
            return UserResponse(
                id=user_profile['id'],
                username=user_profile.get('username') or '',
                email=user_profile.get('email') or user_email or '',
                first_name=user_profile.get('first_name') or '',
                last_name=user_profile.get('last_name') or '',
                is_active=user_profile.get('is_active', True),
                has_completed_onboarding=has_completed_onboarding,
                created_at=user_profile.get('created_at', '2025-01-01T00:00:00')
            )
        
        # Fallback: try to get user from legacy users table if not found above 
        if not legacy_user and not user_profile:
            try:
                legacy_user = await supabase_manager.find_document("users", {"id": user_id})
                logger.info(f"🔍 LEGACY USERS QUERY: SELECT * FROM users WHERE id = '{user_id}'")
                
                if legacy_user:
                    logger.info(f"✅ Found user in legacy users table: {legacy_user.get('username')} (ID: {legacy_user.get('id')})")
                else:
                    logger.info(f"❌ No user found in legacy users table for ID: {user_id}")
            except Exception as legacy_lookup_error:
                logger.error(f"Legacy user lookup failed: {legacy_lookup_error}")
        
        # Return legacy user if found
        if legacy_user:
            # Map level field to has_completed_onboarding (level 2 = completed, level 1 = not completed)
            level = legacy_user.get('level', 1)
            has_completed_onboarding = level >= 2
            
            return UserResponse(
                id=legacy_user['id'],
                username=legacy_user.get('username') or '',
                email=legacy_user.get('email', ''),
                first_name=legacy_user.get('first_name') or '',
                last_name=legacy_user.get('last_name') or '',
                is_active=legacy_user.get('is_active', True),
                has_completed_onboarding=has_completed_onboarding,
                created_at=legacy_user.get('created_at')
            )
        
        # Fallback to user_profiles table
        try:
            profile = await supabase_manager.find_document("user_profiles", {"id": user_id})
            
            if profile:
                logger.info("✅ Found user in user_profiles table")
                # Map level field to has_completed_onboarding (level 2 = completed, level 1 = not completed)
                level = profile.get('level', 1)
                has_completed_onboarding = level >= 2
                
                return UserResponse(
                    id=profile['id'],
                    username=profile.get('username') or '',
                    email=getattr(current_user, 'email', ''),
                    first_name=profile.get('first_name') or '',
                    last_name=profile.get('last_name') or '',
                    is_active=profile.get('is_active', True),
                    has_completed_onboarding=has_completed_onboarding,
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