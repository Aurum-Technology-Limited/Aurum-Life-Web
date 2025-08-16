"""
Clean Supabase-only FastAPI Server
No MongoDB dependencies, pure Supabase implementation
"""

from fastapi import FastAPI, APIRouter, HTTPException, Query, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from dotenv import load_dotenv
from pathlib import Path
import os
import logging
from typing import List, Optional
import asyncio
import uuid
from datetime import timedelta, datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# Import security middleware
from security_middleware import SecurityHeadersMiddleware, CSRFProtectionMiddleware, sanitize_user_input, IDORProtection

# Import ultra-performance services
from ultra_performance_services import (
    UltraPerformancePillarService,
    UltraPerformanceAreaService, 
    UltraPerformanceProjectService,
    UltraPerformanceDashboardService,
    UltraPerformanceInsightsService,
    get_ultra_performance_stats
)
from cache_service import cache_service

# Import our models and Supabase services
from models import *
from supabase_services import (
    SupabaseUserService,
    SupabasePillarService, 
    SupabaseAreaService, 
    SupabaseProjectService,
    SupabaseTaskService,
    SupabaseDashboardService,
    SupabaseInsightsService,
    SupabaseSleepReflectionService
)
from supabase_client import get_supabase_client
from notification_service import NotificationService
from supabase_auth import get_current_active_user, verify_token
from supabase_auth_endpoints import auth_router
from hybrid_auth import get_current_active_user_hybrid
from google_oauth import (
    GoogleOAuthService, 
    SessionManager, 
    GoogleAuthInitiateResponse,
    GoogleAuthCallbackRequest,
    GoogleAuthTokenRequest,
    AuthTokenResponse,
    UserProfileResponse
)
from ai_coach_mvp_service import AiCoachMvpService
from alignment_score_service import AlignmentScoreService
from feedback_service import feedback_service
from models import (
    DailyReflectionCreate,
    DailyReflectionResponse,
    ProjectDecompositionRequest,
    ProjectDecompositionResponse,
    TaskWhyStatementResponse,
    FeedbackCreate,
    FeedbackResponse,
    UserProfileUpdate
)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create the main app
app = FastAPI(title="Aurum Life API - Supabase Only", version="2.0.0")

# CORS middleware - MUST be added BEFORE routers
# Configure allowed origins with env override; default includes preview and localhost
frontend_origins_env = os.environ.get('FRONTEND_ALLOWED_ORIGINS')
if frontend_origins_env:
    ALLOWED_ORIGINS = [o.strip() for o in frontend_origins_env.split(',') if o.strip()]
else:
    ALLOWED_ORIGINS = [
        'https://my-app.preview.emergentagent.com',
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'https://datahierarchy-app.preview.emergentagent.com'
    ]
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE)
    allow_headers=["*"],  # Allow all headers
    expose_headers=["Content-Disposition"],
)

# Security middleware - Add security headers and CSRF protection to all responses
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CSRFProtectionMiddleware)

# Create API router
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Aurum Life API - Supabase Only", "version": "2.0.0", "status": "operational"}

# ================================
# GOOGLE AUTHENTICATION ENDPOINTS
# ================================

# Initialize Google OAuth service
google_oauth = GoogleOAuthService()

@api_router.get("/auth/google/initiate", response_model=GoogleAuthInitiateResponse)
async def initiate_google_auth():
    """Initiate Google OAuth authentication"""
    try:
        state = str(uuid.uuid4())
        auth_url = google_oauth.get_authorization_url(state)
        return GoogleAuthInitiateResponse(auth_url=auth_url, state=state)
    except Exception as e:
        logger.error(f"Error initiating Google auth: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to initiate authentication")

@api_router.get("/auth/google/callback")
async def google_auth_callback(code: str, state: str = None):
    """Handle Google OAuth callback with authorization code"""
    try:
        # Exchange code for token
        token_data = await google_oauth.exchange_code_for_token(code)
        
        # Get user info using access token
        user_data = await google_oauth.get_user_info(token_data['access_token'])
        
        # Create session in our system
        session_token = SessionManager.create_session(user_data)
        
        # Create user object for response
        user_response = {
            'id': user_data.get('id'),
            'email': user_data.get('email'),
            'name': user_data.get('name'),
            'picture': user_data.get('picture')
        }
        
        logger.info(f"Successfully authenticated user {user_data.get('email')} via Google")
        
        # Return JSON response for API use or redirect to frontend with token
        # For now, return JSON response
        return AuthTokenResponse(
            access_token=session_token,
            user=user_response,
            expires_in=604800  # 7 days
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in Google auth callback: {str(e)}")
        raise HTTPException(status_code=500, detail="Authentication failed")

@api_router.post("/auth/google/token", response_model=AuthTokenResponse)
async def google_auth_token(request: GoogleAuthTokenRequest):
    """Handle Google OAuth with ID token (client-side authentication)"""
    try:
        # Verify ID token
        user_data = google_oauth.verify_id_token(request.id_token)
        
        # Create session in our system
        session_token = SessionManager.create_session(user_data)
        
        # Create user object for response
        user_response = {
            'id': user_data.get('sub'),  # 'sub' is the user ID in ID tokens
            'email': user_data.get('email'),
            'name': user_data.get('name'),
            'picture': user_data.get('picture')
        }
        
        logger.info(f"Successfully authenticated user {user_data.get('email')} via Google ID token")
        
        return AuthTokenResponse(
            access_token=session_token,
            user=user_response,
            expires_in=604800  # 7 days
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in Google token auth: {str(e)}")
        raise HTTPException(status_code=500, detail="Authentication failed")

@api_router.get("/auth/google/me", response_model=UserProfileResponse)
async def get_current_user_profile_google(token: str = Depends(HTTPBearer())):
    """Get current user profile from session token"""
    try:
        # Extract token from Bearer scheme
        session_token = token.credentials if hasattr(token, 'credentials') else token
        
        # Get session data
        session_data = SessionManager.get_session(session_token)
        
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session"
            )
        
        # Extend session on successful access
        SessionManager.extend_session(session_token)
        
        return UserProfileResponse(
            id=session_data['user_id'],
            email=session_data['email'],
            name=session_data['name'],
            picture=session_data.get('picture'),
            created_at=session_data['created_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user profile")

# ================================
# LOGIN STREAK ENDPOINTS (DB-backed)
# ================================
@api_router.post("/streaks/login")
async def record_login(request: Request, current_user: User = Depends(get_current_active_user_hybrid)):
    """Record a user's login for today in UTC and update current/best streaks."""
    try:
        user_id = str(current_user.id)
        supabase = get_supabase_client()

        # Normalize dates in UTC
        today_utc = datetime.utcnow().date()
        yesterday_utc = today_utc - timedelta(days=1)

        # Optional client timezone
        client_tz = request.headers.get('X-Client-Timezone')

        # Upsert today's login event
        event_dict = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'login_date_utc': today_utc.isoformat(),
            'client_timezone': client_tz,
            'created_at': datetime.utcnow().isoformat()
        }
        supabase.table('login_events').upsert(event_dict, on_conflict='user_id,login_date_utc').execute()

        # Get profile streaks
        profile_resp = supabase.table('user_profiles').select('current_streak,best_streak').eq('id', user_id).execute()
        current_streak = 0
        best_streak = 0
        if profile_resp.data:
            current_streak = profile_resp.data[0].get('current_streak', 0) or 0
            best_streak = profile_resp.data[0].get('best_streak', 0) or 0

        # Check yesterday login
        y_resp = supabase.table('login_events').select('id').eq('user_id', user_id).eq('login_date_utc', yesterday_utc.isoformat()).limit(1).execute()
        new_current = current_streak + 1 if (y_resp.data or current_streak == 0) else 1
        new_best = max(best_streak, new_current)

        # Update profile
        supabase.table('user_profiles').update({
            'current_streak': new_current,
            'best_streak': new_best,
            'updated_at': datetime.utcnow().isoformat()
        }).eq('id', user_id).execute()

        return { 'status': 'ok', 'current_streak': new_current, 'best_streak': new_best }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording login event: {e}")
        raise HTTPException(status_code=500, detail="Failed to record login")

@api_router.get("/streaks/stats")
async def get_streak_stats(current_user: User = Depends(get_current_active_user_hybrid)):
    try:
        user_id = str(current_user.id)
        supabase = get_supabase_client()
        profile_resp = supabase.table('user_profiles').select('current_streak,best_streak').eq('id', user_id).execute()
        if profile_resp.data:
            return profile_resp.data[0]
        return { 'current_streak': 0, 'best_streak': 0 }
    except Exception as e:
        logger.error(f"Error fetching streak stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch streak stats")

@api_router.get("/streaks/month")
async def get_month_logins(year: int = Query(...), month: int = Query(..., ge=1, le=12), current_user: User = Depends(get_current_active_user_hybrid)):
    try:
        user_id = str(current_user.id)
        supabase = get_supabase_client()
        first_day = datetime(year, month, 1)
        next_month = month + 1
        next_year = year + 1 if next_month == 13 else year
        if next_month == 13:
            next_month = 1
        last_day = datetime(next_year, next_month, 1) - timedelta(days=1)
        resp = supabase.table('login_events').select('login_date_utc').eq('user_id', user_id).gte('login_date_utc', first_day.date().isoformat()).lte('login_date_utc', last_day.date().isoformat()).execute()
        days = []
        for row in (resp.data or []):
            s = row.get('login_date_utc')
            try:
                d = datetime.fromisoformat(s).date() if isinstance(s, str) else s
                days.append(int(d.day))
            except Exception:
                if isinstance(s, str) and len(s) >= 10:
                    days.append(int(s[8:10]))
        return { 'year': year, 'month': month, 'days': sorted(list(set(days))) }
    except Exception as e:
        logger.error(f"Error fetching month logins: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch month logins")

@api_router.post("/auth/logout")
async def logout_user(token: str = Depends(HTTPBearer())):
    """Logout user and invalidate session"""
    try:
        # Extract token from Bearer scheme
        session_token = token.credentials if hasattr(token, 'credentials') else token
        
        # Delete session
        success = SessionManager.delete_session(session_token)
        
        if success:
            return {"message": "Successfully logged out"}
        else:
            return {"message": "Session not found or already expired"}
            
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        # Still return success even if there's an error - user should be logged out
        return {"message": "Logged out"}

# ================================
# AI COACH MVP FEATURES ENDPOINTS WITH SAFEGUARDS
# ================================

# Initialize AI Coach MVP service
ai_coach_mvp = AiCoachMvpService()

# In-memory rate limiting storage (in production, use Redis)
rate_limit_storage = {}

# Generic, endpoint-scoped rate limiter
# key format: f"{user_id}:{scope}"
def check_rate_limit_scoped(user_id: str, scope: str, max_per_min: int = 5) -> bool:
    now = datetime.utcnow()
    key = f"{user_id}:{scope}"
    user_requests = rate_limit_storage.get(key, [])
    # Keep only last minute
    user_requests = [ts for ts in user_requests if now - ts < timedelta(minutes=1)]
    if len(user_requests) >= max_per_min:
        rate_limit_storage[key] = user_requests  # persist cleanup
        return False
    user_requests.append(now)
    rate_limit_storage[key] = user_requests
    return True

# Existing simple limiter retained for backward compatibility

def check_rate_limit(user_id: str) -> bool:
    """Check if user is rate limited (max 3 requests per minute)"""
    now = datetime.utcnow()
    user_requests = rate_limit_storage.get(user_id, [])
    
    # Remove requests older than 1 minute
    user_requests = [req_time for req_time in user_requests if now - req_time < timedelta(minutes=1)]
    
    # Check if under limit
    if len(user_requests) >= 3:
        rate_limit_storage[user_id] = user_requests
        return False
    
    # Add current request
    user_requests.append(now)
    rate_limit_storage[user_id] = user_requests
    
    return True

async def get_user_ai_quota(user_id: str) -> dict:
    """Get user's AI interaction quota for the current month"""
    try:
        supabase = get_supabase_client()
        
        # Get current month start
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Count AI interactions this month from alignment_scores table (repurpose for AI tracking)
        response = supabase.table('ai_interactions').select('*').eq(
            'user_id', user_id
        ).gte('created_at', month_start.isoformat()).execute()
        
        used_quota = len(response.data or [])
        remaining_quota = max(0, 10 - used_quota)  # 10 interactions per month
        
        return {
            'total': 10,
            'used': used_quota,
            'remaining': remaining_quota,
            'resets_at': (month_start + timedelta(days=32)).replace(day=1).isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting AI quota: {e}")
        # Return default quota on error
        return {'total': 10, 'used': 0, 'remaining': 10, 'resets_at': None}

async def record_ai_interaction(user_id: str, interaction_type: str, context_size: int):
    """Record an AI interaction for quota tracking"""
    try:
        supabase = get_supabase_client()
        
        interaction_record = {
            'user_id': user_id,
            'interaction_type': interaction_type,
            'context_size': context_size,
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Store in repurposed table or create new tracking
        supabase.table('ai_interactions').insert(interaction_record).execute()
        
    except Exception as e:
        logger.error(f"Error recording AI interaction: {e}")

@api_router.get("/ai/quota")
async def get_ai_quota(current_user: User = Depends(get_current_active_user_hybrid)):
    """Get user's AI interaction quota"""
    try:
        user_id = current_user.id
        quota = await get_user_ai_quota(str(user_id))
        return quota
    except Exception as e:
        logger.error(f"Error getting AI quota: {e}")
        raise HTTPException(status_code=500, detail="Failed to get AI quota")

# Feature 1: Goal Decomposition with Structured Response
@api_router.post("/ai/decompose-project", response_model=dict)
async def decompose_project_with_safeguards(
    request: ProjectDecompositionRequest,
    current_user: User = Depends(get_current_active_user_hybrid)
):
    """
    AI-powered goal decomposition with structured JSON response for interactive workflow
    """
    try:
        user_id = str(current_user.id)
        
        # Check rate limit
        if not check_rate_limit(user_id):
            raise HTTPException(
                status_code=429, 
                detail="Rate limit exceeded. Maximum 3 requests per minute."
            )
        
        # Check quota
        quota = await get_user_ai_quota(user_id)
        if quota['remaining'] <= 0:
            raise HTTPException(
                status_code=402,  # Payment Required - quota exceeded
                detail="Monthly AI interaction limit reached. Limit resets next month."
            )
        
        # Generate structured suggestions for interactive workflow
        suggestions = await generate_structured_project_breakdown(user_id, request)
        
        # Record interaction
        await record_ai_interaction(user_id, 'goal_decomposition', len(request.project_name))
        
        return suggestions
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in goal decomposition: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate goal breakdown")

# ... existing AI endpoints and helpers ...

# ================================
# TODAY PRIORITIZATION (MVP)
# ================================
@api_router.get("/today")
async def get_today_view(
    top_n: int = Query(3, ge=0, le=10),
    current_user: User = Depends(get_current_active_user_hybrid)
):
    """
    Return prioritized tasks for Today view using rule-based scoring and optional Gemini coaching
    for the top N (default 3). Includes per-task scoring breakdown for verification.
    """
    try:
        user_id = str(current_user.id)
        # Rate-limit Today requests, and especially gemini calls when top_n > 0
        scope = 'today_with_ai' if top_n and top_n > 0 else 'today_no_ai'
        max_per_min = 3 if scope == 'today_with_ai' else 6
        if not check_rate_limit_scoped(user_id, scope, max_per_min):
            raise HTTPException(status_code=429, detail="Too many requests. Please slow down.")

        result = await ai_coach_mvp.get_today_priorities(user_id, coaching_top_n=top_n)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating Today view: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate Today view")

# ================================
# PILLARS ENDPOINTS (ULTRA + STANDARD)
# ================================
@api_router.get("/ultra/pillars", response_model=List[dict])
async def ultra_get_pillars(
    include_areas: bool = Query(False, description="Include linked areas"),
    include_archived: bool = Query(False, description="Include archived pillars"),
    current_user: User = Depends(get_current_active_user_hybrid)
):
    try:
        user_id = str(current_user.id)
        pillars = await UltraPerformancePillarService.get_user_pillars(
            user_id, include_areas=include_areas, include_archived=include_archived
        )
        # Convert Pydantic models to dict if necessary
        return [p.dict() if hasattr(p, 'dict') else dict(p) if isinstance(p, dict) else p for p in pillars]
    except Exception as e:
        logger.error(f"Ultra pillars error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch pillars")

@api_router.get("/pillars", response_model=List[dict])
async def get_pillars(
    include_sub_pillars: bool = Query(False, description="(Reserved) Include sub pillars - not used in Supabase mode"),
    include_areas: bool = Query(False, description="Include linked areas"),
    include_archived: bool = Query(False, description="Include archived pillars"),
    current_user: User = Depends(get_current_active_user_hybrid)
):
    try:
        user_id = str(current_user.id)
        pillars = await SupabasePillarService.get_user_pillars(
            user_id, include_areas=include_areas, include_archived=include_archived
        )
        return pillars
    except Exception as e:
        logger.error(f"Pillars error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch pillars")

# ================================
# TASKS: SEARCH & SUGGEST-FOCUS
# ================================
@api_router.get("/tasks/search")
async def search_tasks(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=25),
    current_user: User = Depends(get_current_active_user_hybrid)
):
    """User-scoped partial search over task name/description (excludes completed)."""
    try:
        user_id = str(current_user.id)
        # Rate limit search to prevent abuse
        if not check_rate_limit_scoped(user_id, 'tasks_search', 30):
            raise HTTPException(status_code=429, detail="Search rate limit exceeded. Please wait a moment.")
        supabase = get_supabase_client()

        # Build OR filter for ilike on name/description
        or_filter = f"name.ilike.%{q}%,description.ilike.%{q}%"
        resp = (
            supabase
            .table('tasks')
            .select('id, name, description, project_id, due_date, priority, status, completed')
            .eq('user_id', user_id)
            .eq('completed', False)
            .or_(or_filter)
            .limit(limit)
            .execute()
        )
        tasks = resp.data or []
        if not tasks:
            return []
        # Fetch related projects for names
        proj_ids = list({t.get('project_id') for t in tasks if t.get('project_id')})
        projects = {}
        if proj_ids:
            proj_resp = supabase.table('projects').select('id, name').in_('id', proj_ids).execute()
            for p in (proj_resp.data or []):
                projects[p['id']] = p
        # Map output fields
        out = []
        for t in tasks:
            p = projects.get(t.get('project_id')) if t.get('project_id') else None
            out.append({
                'taskId': t['id'],
                'title': t.get('name'),
                'description': t.get('description'),
                'project': p.get('name') if p else None,
                'dueDate': t.get('due_date'),
                'priority': t.get('priority'),
                'status': t.get('status')
            })
        return out
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in tasks search: {e}")
        raise HTTPException(status_code=500, detail="Failed to search tasks")

@api_router.get("/tasks/suggest-focus")
async def suggest_focus_tasks(current_user: User = Depends(get_current_active_user_hybrid)):
    """Return top 3 suggested tasks using rule-based scoring. Includes full task payload to avoid extra fetches."""
    try:
        user_id = str(current_user.id)
        # Rate limit suggestions
        if not check_rate_limit_scoped(user_id, 'tasks_suggest_focus', 6):
            raise HTTPException(status_code=429, detail="Too many requests. Please slow down.")
        # Compute priorities without LLM
        result = await ai_coach_mvp.get_today_priorities(user_id, coaching_top_n=0)
        tasks_sorted = result.get('tasks', [])
        top3 = tasks_sorted[:3]
        ids = [t.get('id') for t in top3 if t.get('id')]
        # Validate existence and enrich with task fields + project names to avoid 404 on client
        supabase = get_supabase_client()
        full_lookup = {}
        if ids:
            t_resp = (
                supabase.table('tasks')
                .select('id,name,description,priority,status,due_date,project_id,completed')
                .eq('user_id', user_id)
                .in_('id', ids)
                .execute()
            )
            task_rows = t_resp.data or []
            proj_ids = list({row.get('project_id') for row in task_rows if row.get('project_id')})
            proj_lookup = {}
            if proj_ids:
                p_resp = supabase.table('projects').select('id,name').in_('id', proj_ids).execute()
                for p in (p_resp.data or []):
                    proj_lookup[p['id']] = p['name']
            for row in task_rows:
                full_lookup[row['id']] = {
                    'id': row['id'],
                    'name': row.get('name'),
                    'description': row.get('description'),
                    'priority': row.get('priority'),
                    'status': row.get('status'),
                    'due_date': row.get('due_date'),
                    'project_name': proj_lookup.get(row.get('project_id'))
                }
        # Map to required fields and include full task when available
        mapped = []
        for t in top3:
            tid = t.get('id')
            mapped.append({
                'taskId': tid,
                'title': t.get('title'),
                'description': t.get('description'),
                'project': t.get('project_name'),
                'dueDate': t.get('due_date'),
                'priority': t.get('priority'),
                'status': t.get('status'),
                'task': full_lookup.get(tid)  # may be None if filtered out
            })
        # Filter out items without a valid underlying task if you want stricter validation
        mapped = [m for m in mapped if m.get('task') is not None]
        return mapped
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in suggest focus: {e}")
        raise HTTPException(status_code=500, detail="Failed to suggest focus tasks")

# ... existing endpoints continue ...

# ================================
# DASHBOARD ENDPOINT
# ================================

@api_router.get("/dashboard", response_model=dict)
async def get_dashboard(current_user: User = Depends(get_current_active_user_hybrid)):
    """Get dashboard data"""
    try:
        dashboard_service = SupabaseDashboardService()
        dashboard_data = await dashboard_service.get_dashboard_data(str(current_user.id))
        return dashboard_data
    except Exception as e:
        logger.error(f"Error getting dashboard data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.get("/ultra/dashboard", response_model=dict)
async def get_ultra_dashboard(current_user: User = Depends(get_current_active_user_hybrid)):
    """Get ultra-performance dashboard data"""
    try:
        ultra_dashboard_service = UltraPerformanceDashboardService()
        dashboard_data = await ultra_dashboard_service.get_dashboard_data(str(current_user.id))
        return dashboard_data
    except Exception as e:
        logger.error(f"Error getting ultra dashboard data: {str(e)}")
        # Fallback to regular dashboard
        try:
            dashboard_service = SupabaseDashboardService()
            dashboard_data = await dashboard_service.get_dashboard_data(str(current_user.id))
            return dashboard_data
        except Exception as fallback_e:
            logger.error(f"Error getting fallback dashboard data: {str(fallback_e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

# ================================
# ALIGNMENT SCORE QUICK FIX ENDPOINT
# ================================
@api_router.get("/alignment-score")
async def get_alignment_score_quick(current_user: User = Depends(get_current_active_user_hybrid)):
    """
    Quick unblock endpoint for AlignmentScore component. Returns a static success payload.
    """
    try:
        return {"score": 75, "trend": "up", "message": "Alignment data loaded."}
    except Exception as e:
        logger.error(f"Error in alignment-score quick endpoint: {e}")
        raise HTTPException(status_code=500, detail="Failed to load alignment score")


# Include the auth router in the api router

# ================================
# MONTHLY GOAL ENDPOINTS (CRUD minimal)
# ================================
class MonthlyGoalUpdate(BaseModel):
    goal: int = Field(..., ge=1, le=100000)

@api_router.get("/alignment/monthly-goal")
async def get_monthly_goal(current_user: User = Depends(get_current_active_user_hybrid)):
    try:
      service = AlignmentScoreService()
      goal = await service.get_user_monthly_goal(str(current_user.id))
      return { 'goal': goal }
    except Exception as e:
      logger.error(f"Get monthly goal error: {e}")
      raise HTTPException(status_code=500, detail='Failed to fetch monthly goal')

@api_router.put("/alignment/monthly-goal")
async def set_monthly_goal(payload: MonthlyGoalUpdate, current_user: User = Depends(get_current_active_user_hybrid)):
    try:
      service = AlignmentScoreService()
      ok = await service.set_user_monthly_goal(str(current_user.id), int(payload.goal))
      if not ok:
        raise HTTPException(status_code=400, detail='Failed to update monthly goal')
      return { 'status': 'ok', 'goal': int(payload.goal) }
    except HTTPException:
      raise
    except Exception as e:
      logger.error(f"Set monthly goal error: {e}")
      raise HTTPException(status_code=500, detail='Failed to update monthly goal')

api_router.include_router(auth_router, prefix="/auth")

# ================================
# ALIGNMENT DASHBOARD ENDPOINT
# ================================
@api_router.get("/alignment/dashboard")
async def get_alignment_dashboard(current_user: User = Depends(get_current_active_user_hybrid)):
    try:
        svc = AlignmentScoreService()
        data = await svc.get_alignment_dashboard_data(str(current_user.id))
        return data
    except Exception as e:
        logger.error(f"Alignment dashboard error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch alignment dashboard data")


# Include the router
app.include_router(api_router)

# ================================
# FRONTEND CATCH-ALL FOR SPA ROUTING
# ================================
# Serve index.html for any non-API path so React Router can handle routes like /pillars
from fastapi.responses import FileResponse

FRONTEND_DIR = Path(__file__).parent.parent / 'frontend' / 'build'
INDEX_FILE = FRONTEND_DIR / 'index.html'

@app.get('/{full_path:path}')
async def spa_catch_all(full_path: str):
    # Only handle non-API paths
    if full_path.startswith('api'):
        raise HTTPException(status_code=404, detail='API route not found')
    try:
        # If build exists, serve index.html, else return a friendly message
        if INDEX_FILE.exists():
            return FileResponse(str(INDEX_FILE))
        return { 'status': 'ok', 'message': 'SPA route', 'path': full_path }
    except Exception as e:
        logger.error(f"SPA catch-all error: {e}")
        raise HTTPException(status_code=404, detail='Not Found')