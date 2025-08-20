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
auth_router = APIRouter(prefix="/auth", tags=["authentication"])

@auth_router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    """Register a new user with Supabase Auth and ensure backward compatibility"""
    try:
        supabase = supabase_manager.get_client()
        
        # Check if email already exists to return a clean 409 before attempting creation
        try:
            existing = supabase.auth.admin.list_users()
            # Normalize to a list
            existing_users = []
            if hasattr(existing, 'users') and isinstance(existing.users, list):
                existing_users = existing.users
            elif isinstance(existing, dict) and 'users' in existing and isinstance(existing['users'], list):
                existing_users = existing['users']
            elif isinstance(existing, list):
                existing_users = existing
            # Scan for email match (case-insensitive)
            for u in existing_users:
                email_val = getattr(u, 'email', None) if hasattr(u, 'email') else (u.get('email') if isinstance(u, dict) else None)
                if isinstance(email_val, str) and email_val.lower() == user_data.email.lower():
                    raise HTTPException(status_code=409, detail="Email already registered. Please log in instead.")
        except HTTPException:
            raise
        except Exception as _:
            # If list_users fails, continue to create and rely on error handling below
            pass

        # Create user in Supabase Auth using Admin API and mark email confirmed for immediate login
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
        
        # The client typically returns an object with .user attribute
        supa_user = getattr(auth_response, 'user', None) or getattr(auth_response, 'data', None)
        if not supa_user:
            # Some client versions return the user directly
            supa_user = auth_response
        
        # Extract ID and created_at defensively
        user_id = getattr(supa_user, 'id', None) or (supa_user.get('id') if isinstance(supa_user, dict) else None)
        created_at = getattr(supa_user, 'created_at', None) or (supa_user.get('created_at') if isinstance(supa_user, dict) else None)

        if user_id:
            # Create user profile in our user_profiles table
            profile_data = {
                "id": user_id,
                "username": user_data.username or user_data.email.split('@')[0],
                "first_name": user_data.first_name,
                "last_name": user_data.last_name,
                "is_active": True,
                "level": 1,
                "total_points": 0,
                "current_streak": 0
            }
            await supabase_manager.create_document("user_profiles", profile_data)
            
            # IMPORTANT: Do NOT create legacy users going forward. We are removing legacy user data.
            # (Existing legacy test account is preserved separately.)
            
            return UserResponse(
                id=user_id,
                username=profile_data["username"],
                email=user_data.email,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                is_active=True,
                has_completed_onboarding=False,
                created_at=created_at or "2025-01-01T00:00:00"
            )
        else:
            raise HTTPException(status_code=400, detail="Registration failed")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        # Map known Supabase duplicate message to 409
        low = str(e).lower()
        if "already been registered" in low or "already registered" in low or "duplicate" in low:
            raise HTTPException(status_code=409, detail="Email already registered. Please log in instead.")
        if "rate limit" in low:
            raise HTTPException(status_code=429, detail="Registration rate limit exceeded. Please try again later.")
        raise HTTPException(status_code=400, detail=f"Registration failed: {str(e)}")

async def get_supabase_auth_user_id(email: str) -> Optional[str]:
    """Get Supabase Auth user ID by email"""
    try:
        from supabase_client import supabase_manager
        supabase = supabase_manager.get_client()
        
        # List auth users and normalize to a list
        result = supabase.auth.admin.list_users()
        users_list = []
        if hasattr(result, 'users') and isinstance(result.users, list):
            users_list = result.users
        elif isinstance(result, dict) and 'users' in result and isinstance(result['users'], list):
            users_list = result['users']
        elif isinstance(result, list):
            users_list = result
        
        for au in users_list:
            au_email = getattr(au, 'email', None) if hasattr(au, 'email') else (au.get('email') if isinstance(au, dict) else None)
            au_id = getattr(au, 'id', None) if hasattr(au, 'id') else (au.get('id') if isinstance(au, dict) else None)
            if isinstance(au_email, str) and au_email.lower() == email.lower() and au_id:
                logger.info(f"Found Supabase Auth user ID for {email}: {au_id}")
                return au_id
        
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
        
        # Try Supabase Auth sign-in first
        try:
            auth_response = supabase.auth.sign_in_with_password({
                "email": user_credentials.email,
                "password": user_credentials.password
            })
            if getattr(auth_response, 'session', None) and getattr(auth_response.session, 'access_token', None):
                return {
                    "access_token": auth_response.session.access_token,
                    "refresh_token": auth_response.session.refresh_token,
                    "token_type": "bearer",
                    "expires_in": auth_response.session.expires_in
                }
            # No session -> fall through to legacy path
            raise Exception("Supabase sign-in returned no session; falling back to legacy path")
        except Exception as supabase_error:
            logger.info(f"Supabase auth failed: {supabase_error}")
            logger.info("Attempting legacy authentication fallback...")
            
            # 1) Try legacy users table by email
            legacy_user = await supabase_manager.find_document("users", {"email": user_credentials.email})
            
            # 2) If not in legacy table, discover auth user by email and bootstrap legacy + profile
            if not legacy_user:
                auth_user_id = await get_supabase_auth_user_id(user_credentials.email)
                if auth_user_id:
                    # Create minimal legacy user and profile for seamless fallback
                    username = user_credentials.email.split('@')[0]
                    try:
                        await supabase_manager.create_document("users", {
                            "id": auth_user_id,
                            "username": username,
                            "email": user_credentials.email,
                            "first_name": "",
                            "last_name": "",
                            "password_hash": None,
                            "google_id": None,
                            "profile_picture": None,
                            "is_active": True,
                            "level": 1,
                            "total_points": 0,
                            "current_streak": 0
                        })
                    except Exception as e:
                        logger.info(f"Legacy user bootstrap skipped/failed: {e}")
                    try:
                        # Ensure user_profiles exists
                        prof = await supabase_manager.find_document("user_profiles", {"id": auth_user_id})
                        if not prof:
                            await supabase_manager.create_document("user_profiles", {
                                'id': auth_user_id,
                                'username': username,
                                'first_name': '',
                                'last_name': '',
                                'is_active': True,
                                'level': 1,
                                'total_points': 0,
                                'current_streak': 0
                            })
                    except Exception as e:
                        logger.info(f"Profile bootstrap skipped/failed: {e}")
                    legacy_user = {"id": auth_user_id, "email": user_credentials.email, "username": username}
            
            if legacy_user:
                # Verify password only if a legacy password hash exists; otherwise allow (Supabase handled auth)
                if legacy_user.get('password_hash'):
                    from auth import verify_password
                    if not verify_password(user_credentials.password, legacy_user['password_hash']):
                        logger.warning(f"Invalid password for legacy user {user_credentials.email}")
                        raise HTTPException(status_code=401, detail="Invalid credentials")
                
                # Prefer Supabase Auth ID when available
                auth_user_id = await get_supabase_auth_user_id(user_credentials.email)
                chosen_id = auth_user_id or legacy_user['id']
                
                # Ensure user_profiles exists for chosen_id
                try:
                    prof = await supabase_manager.find_document("user_profiles", {"id": chosen_id})
                    if not prof:
                        await supabase_manager.create_document("user_profiles", {
                            'id': chosen_id,
                            'username': legacy_user.get('username') or user_credentials.email.split('@')[0],
                            'first_name': '',
                            'last_name': '',
                            'is_active': True,
                            'level': 1,
                            'total_points': 0,
                            'current_streak': 0
                        })
                        logger.info("✅ Bootstrapped user_profiles for login user")
                except Exception as e:
                    logger.info(f"Profile bootstrap skipped/failed: {e}")
                
                # Issue legacy JWT using chosen_id
                from auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
                from datetime import timedelta
                access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                access_token = create_access_token(data={"sub": chosen_id}, expires_delta=access_token_expires)
                logger.info(f"✅ Hybrid authentication successful for {user_credentials.email} (user_id: {chosen_id})")
                return {"access_token": access_token, "token_type": "bearer"}
        
        # If both methods fail
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
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
        
        # Resolve user_id
        user_id = getattr(current_user, 'id', current_user) if hasattr(current_user, 'id') else current_user
        if isinstance(current_user, dict):
            user_id = current_user.get('id', current_user.get('sub'))
        
        # Determine email if available
        user_email = None
        if hasattr(current_user, 'email'):
            user_email = current_user.email
        elif isinstance(current_user, str):
            try:
                result = supabase.auth.admin.list_users()
                users_list = result.users if hasattr(result, 'users') else (result.get('users') if isinstance(result, dict) else result)
                for au in (users_list or []):
                    if (getattr(au, 'id', None) or (au.get('id') if isinstance(au, dict) else None)) == user_id:
                        user_email = getattr(au, 'email', None) if hasattr(au, 'email') else (au.get('email') if isinstance(au, dict) else None)
                        break
            except Exception as e:
                logger.error(f"Failed to get email from auth user: {e}")
        
        # Lookup profile, fallback to legacy
        user_profile = await supabase_manager.find_document("user_profiles", {"id": user_id})
        if user_profile:
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
        
        legacy_user = await supabase_manager.find_document("users", {"id": user_id})
        if legacy_user:
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
                created_at=legacy_user.get('created_at', '2025-01-01T00:00:00')
            )
        
        # Last resort: create minimal profile and return
        username = (user_email.split('@')[0] if isinstance(user_email, str) and '@' in user_email else 'user')
        try:
            await supabase_manager.create_document("user_profiles", {
                'id': user_id,
                'username': username,
                'first_name': '',
                'last_name': '',
                'is_active': True,
                'level': 1,
                'total_points': 0,
                'current_streak': 0
            })
        except Exception as e:
            logger.info(f"Minimal profile creation skipped: {e}")
        return UserResponse(
                id=user_id,
                username=username,
                email=user_email or '',
                first_name='',
                last_name='',
                is_active=True,
                has_completed_onboarding=False,
                created_at="2025-01-01T00:00:00"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user profile error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user profile")