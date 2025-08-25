"""
Supabase Authentication Endpoints
Replaces traditional JWT auth with Supabase Auth integration
"""

from fastapi import APIRouter, HTTPException, status, Request, Depends
from pydantic import BaseModel
from supabase_client import supabase_manager
from supabase_auth import verify_token, get_current_active_user
from models import UserCreate, UserLogin, UserResponse, User
import logging

logger = logging.getLogger(__name__)

auth_router = APIRouter(prefix="/auth", tags=["authentication"])

class RefreshRequest(BaseModel):
    refresh_token: str

class ForgotPasswordRequest(BaseModel):
    email: str

class UpdatePasswordRequest(BaseModel):
    new_password: str

@auth_router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    try:
        supabase = supabase_manager.get_client()
        try:
            existing = supabase.auth.admin.list_users()
            existing_users = existing.users if hasattr(existing, 'users') else (existing.get('users') if isinstance(existing, dict) else existing)
            for u in (existing_users or []):
                email_val = getattr(u, 'email', None) if hasattr(u, 'email') else (u.get('email') if isinstance(u, dict) else None)
                if isinstance(email_val, str) and email_val.lower() == user_data.email.lower():
                    raise HTTPException(status_code=409, detail="Email already registered. Please log in instead.")
        except HTTPException:
            raise
        except Exception:
            pass
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
        supa_user = getattr(auth_response, 'user', None) or getattr(auth_response, 'data', None) or auth_response
        user_id = getattr(supa_user, 'id', None) or (supa_user.get('id') if isinstance(supa_user, dict) else None)
        created_at = getattr(supa_user, 'created_at', None) or (supa_user.get('created_at') if isinstance(supa_user, dict) else None)
        if user_id:
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
        raise HTTPException(status_code=400, detail="Registration failed")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        low = str(e).lower()
        if "already" in low and "register" in low:
            raise HTTPException(status_code=409, detail="Email already registered. Please log in instead.")
        raise HTTPException(status_code=400, detail=f"Registration failed: {str(e)}")

@auth_router.post("/login")
async def login_user(user_credentials: UserLogin):
    try:
        supabase = supabase_manager.get_client()
        auth_response = supabase.auth.sign_in_with_password({
            "email": user_credentials.email,
            "password": user_credentials.password
        })
        if getattr(auth_response, 'session', None) and getattr(auth_response.session, 'access_token', None):
            return {
                "access_token": auth_response.session.access_token,
                "refresh_token": getattr(auth_response.session, 'refresh_token', None),
                "token_type": "bearer",
                "expires_in": getattr(auth_response.session, 'expires_in', 3600)
            }
        raise HTTPException(status_code=401, detail="Invalid credentials")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

@auth_router.post("/refresh")
async def refresh_session(payload: RefreshRequest):
    try:
        supabase = supabase_manager.get_client()
        refreshed = None
        try:
            refreshed = supabase.auth.refresh_session({"refresh_token": payload.refresh_token})
        except Exception as e:
            logger.info(f"Primary refresh method failed: {e}")
            try:
                refreshed = supabase.auth.set_session({"refresh_token": payload.refresh_token, "access_token": ""})
            except Exception as e2:
                logger.error(f"Fallback refresh failed: {e2}")
                raise HTTPException(status_code=401, detail="Failed to refresh session")
        session = getattr(refreshed, 'session', None) or getattr(refreshed, 'data', None) or refreshed
        access_token = getattr(session, 'access_token', None) if session else None
        refresh_token = getattr(session, 'refresh_token', None) if session else None
        expires_in = getattr(session, 'expires_in', None) if session else 3600
        if not access_token:
            raise HTTPException(status_code=401, detail="Failed to refresh session")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token or payload.refresh_token,
            "token_type": "bearer",
            "expires_in": expires_in
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Refresh session error: {e}")
        raise HTTPException(status_code=401, detail="Failed to refresh session")

@auth_router.post("/forgot-password")
async def forgot_password(payload: ForgotPasswordRequest, request: Request):
    """Trigger password reset. Attempts both standard reset and admin-generated link with redirect.
    In preview/local environments, always include a recovery_url fallback so users can proceed without email.
    """
    try:
        supabase = supabase_manager.get_client()
        # Build redirect_to from request origin if present, with fallback to preview domain
        origin = request.headers.get('origin')
        if not origin:
            scheme = request.url.scheme
            host = request.headers.get('host')
            if scheme and host:
                origin = f"{scheme}://{host}"
        
        # Fix for localhost issue - ensure we use the correct preview domain for redirect
        if origin and ("localhost" in origin or "127.0.0.1" in origin):
            origin = "https://prodflow-auth.preview.emergentagent.com"
        elif not origin:
            # Default to preview domain if no origin detected
            origin = "https://prodflow-auth.preview.emergentagent.com"
            
        redirect_to = f"{origin}/reset-password" if origin else None

        # Determine if we should force include recovery_url for dev/preview domains
        dev_like = False
        try:
            if origin:
                dev_like = (".preview.emergentagent.com" in origin) or ("localhost" in origin)
        except Exception:
            dev_like = False

        # Try standard reset flow (this triggers the provider to send an email)
        try:
            if redirect_to:
                supabase.auth.reset_password_for_email(payload.email, options={"redirect_to": redirect_to})
            else:
                supabase.auth.reset_password_for_email(payload.email)
            logger.info("Supabase reset_password_for_email invoked successfully")
        except Exception as e:
            logger.info(f"Primary reset_password_for_email failed or not supported: {e}")
        
        # Generate a recovery link via admin API (does not send email). Always attempt; include in response for dev_like.
        recovery_url = None
        gen_error = None
        try:
            opts = {"email": payload.email, "type": "recovery"}
            if redirect_to:
                opts["options"] = {"redirect_to": redirect_to}
            gen = supabase.auth.admin.generate_link(opts)
            # normalize return - check for different response structures
            if hasattr(gen, 'properties') and hasattr(gen.properties, 'action_link'):
                recovery_url = gen.properties.action_link
            elif hasattr(gen, 'data') and isinstance(gen.data, dict):
                recovery_url = gen.data.get('action_link') or gen.data.get('properties', {}).get('action_link')
            elif hasattr(gen, 'action_link'):
                recovery_url = gen.action_link
            elif isinstance(gen, dict):
                recovery_url = gen.get('action_link') or gen.get('data', {}).get('action_link')
            logger.info(f"Generated recovery link via admin API: {bool(recovery_url)}")
        except Exception as e:
            gen_error = str(e)
            logger.info(f"Admin generate_link not available or failed: {e}")
        
        resp = {"success": True, "message": "If an account exists, a password reset email has been sent."}
        if recovery_url and dev_like:
            # Provide dev fallback link so user can proceed immediately on preview/local
            resp["recovery_url"] = recovery_url
        if dev_like and not recovery_url and gen_error:
            resp["debug"] = {"recovery_generate_error": gen_error}
        return resp
    except Exception as e:
        logger.error(f"Forgot password error: {e}")
        # Always mask existence of email for security
        return {"success": True, "message": "If an account exists, a password reset email has been sent."}

@auth_router.post("/update-password")
async def update_password(payload: UpdatePasswordRequest, current_user: User = Depends(get_current_active_user)):
    """Update password for the current authenticated user (used after reset link)."""
    try:
        supabase = supabase_manager.get_client()
        res = supabase.auth.update_user({"password": payload.new_password})
        return {"success": True}
    except Exception as e:
        logger.error(f"Update password error: {e}")
        raise HTTPException(status_code=400, detail="Failed to update password")

@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_profile(request: Request):
    try:
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="No authorization token provided")
        token = authorization.split(" ")[1]
        current_user = await verify_token(token)
        supabase = supabase_manager.get_client()
        user_id = getattr(current_user, 'id', None) or (current_user.get('id') if isinstance(current_user, dict) else None)
        if not user_id:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        profile = await supabase_manager.find_document("user_profiles", {"id": user_id})
        if not profile:
            username = current_user.email.split('@')[0] if hasattr(current_user, 'email') else 'user'
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
            profile = await supabase_manager.find_document("user_profiles", {"id": user_id})
        has_completed_onboarding = (profile.get('level', 1) >= 2)
        return UserResponse(
            id=profile['id'],
            username=profile.get('username') or '',
            email=current_user.email if hasattr(current_user, 'email') else (profile.get('email') or ''),
            first_name=profile.get('first_name') or '',
            last_name=profile.get('last_name') or '',
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
    try:
        user_id = str(current_user.id)
        profile = await supabase_manager.find_document("user_profiles", {"id": user_id})
        if not profile:
            await supabase_manager.create_document("user_profiles", {
                'id': user_id,
                'username': '',
                'first_name': '',
                'last_name': '',
                'is_active': True,
                'level': 2,
                'total_points': 0,
                'current_streak': 0
            })
        else:
            level = profile.get('level', 1)
            if level < 2:
                await supabase_manager.update_document("user_profiles", {"id": user_id}, {"level": 2})
        return {"success": True}
    except Exception as e:
        logger.error(f"Failed to complete onboarding: {e}")
        raise HTTPException(status_code=500, detail="Failed to complete onboarding")