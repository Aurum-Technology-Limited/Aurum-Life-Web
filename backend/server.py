from fastapi import FastAPI, APIRouter, HTTPException, Query, Depends, status, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from pathlib import Path
import os
import logging
import asyncio
from typing import List, Optional
from datetime import timedelta, datetime
import time
import uuid

# Import our models and services
from supabase_client import supabase_manager, find_document, find_documents
from models import *
from optimized_services import (
    OptimizedPillarService, 
    OptimizedAreaService, 
    OptimizedProjectService,
    OptimizedStatsService
)
from performance_monitor import perf_monitor
from services import (
    UserService, TaskService, JournalService, 
    CourseService, RecurringTaskService, InsightsService, 
    ResourceService, StatsService, PillarService, AreaService, ProjectService,
    ProjectTemplateService, GoogleAuthService
)
from supabase_services import SupabasePillarService, SupabaseAreaService, SupabaseProjectService
from notification_service import notification_service
from auth import get_current_active_user as old_get_current_active_user, verify_token as old_verify_token, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, verify_password
from supabase_auth import get_current_active_user, verify_token
from supabase_auth_endpoints import auth_router
from analytics_service import AnalyticsService
from alignment_score_service import AlignmentScoreService
from ai_coach_mvp_service import AiCoachMvpService

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create the main app
app = FastAPI(title="Aurum Life API", version="1.0.0")

# CORS middleware - MUST be added BEFORE routers
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],  # Allow all origins for development
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE)
    allow_headers=["*"],  # Allow all headers
)

# Create API router
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default user ID for demo (in real app, this would come from authentication)
DEFAULT_USER_ID = "demo-user-123"

# Use Supabase Auth system for production
# get_current_active_user and verify_token are now imported from supabase_auth

# Hybrid authentication dependency for API endpoints
async def get_current_active_user_hybrid(request: Request) -> User:
    """Get current active user using hybrid authentication (Supabase + Legacy JWT)"""
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
            current_user = await verify_token(token)
            user_id = current_user.id
            logger.info("✅ Verified Supabase token for API endpoint")
        except Exception as supabase_error:
            logger.info(f"Supabase token verification failed: {supabase_error}")
            
            # Try legacy JWT token verification
            try:
                from auth import jwt, SECRET_KEY, ALGORITHM
                
                # Decode JWT token directly
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                user_id = payload.get("sub")
                if user_id is None:
                    raise HTTPException(status_code=401, detail="Could not validate credentials")
                
                logger.info("✅ Verified legacy JWT token for API endpoint")
            except Exception as legacy_error:
                logger.info(f"Legacy token verification failed: {legacy_error}")
                raise HTTPException(status_code=401, detail="Could not validate credentials")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        
        # Get user data from user_profiles table (which uses auth user IDs)
        try:
            user_profile = await supabase_manager.find_document("user_profiles", {"id": user_id})
            
            if user_profile:
                # Convert to User model using profile data
                from models import User
                return User(
                    id=user_profile['id'],
                    username=user_profile.get('username', ''),
                    email='',  # Email not stored in user_profiles
                    first_name=user_profile.get('first_name', ''),
                    last_name=user_profile.get('last_name', ''),
                    password_hash='',  # Not needed for auth user
                    google_id='',
                    profile_picture='',
                    is_active=user_profile.get('is_active', True),
                    level=user_profile.get('level', 1),
                    total_points=user_profile.get('total_points', 0),
                    current_streak=user_profile.get('current_streak', 0),
                    created_at=user_profile.get('created_at'),
                    updated_at=user_profile.get('updated_at')
                )
        except Exception as profile_lookup_error:
            logger.info(f"User_profiles lookup failed: {profile_lookup_error}")
            
        # Fallback: try legacy users table
        try:
            legacy_user = await supabase_manager.find_document("users", {"id": user_id})
            
            if legacy_user:
                # Convert to User model
                from models import User
                return User(
                    id=legacy_user['id'],
                    username=legacy_user.get('username', ''),
                    email=legacy_user.get('email', ''),
                    first_name=legacy_user.get('first_name', ''),
                    last_name=legacy_user.get('last_name', ''),
                    password_hash=legacy_user.get('password_hash'),
                    google_id=legacy_user.get('google_id'),
                    profile_picture=legacy_user.get('profile_picture'),
                    is_active=legacy_user.get('is_active', True),
                    level=legacy_user.get('level', 1),
                    total_points=legacy_user.get('total_points', 0),
                    current_streak=legacy_user.get('current_streak', 0),
                    created_at=legacy_user.get('created_at'),
                    updated_at=legacy_user.get('updated_at')
                )
        except Exception as lookup_error:
            logger.error(f"Legacy user lookup failed: {lookup_error}")
        
        # User not found
        raise HTTPException(status_code=404, detail="User not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Hybrid authentication error: {e}")
        raise HTTPException(status_code=401, detail="Could not validate credentials")

# Use hybrid authentication for all endpoints
get_current_active_user = get_current_active_user_hybrid

# Health check endpoints
@api_router.get("/")
async def root():
    return {"message": "Aurum Life API is running", "version": "1.0.0"}

@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Aurum Life API", "version": "1.0.0", "status": "running"}

@app.get("/favicon.ico")
async def favicon():
    """Favicon endpoint to prevent 404 errors"""
    return {"message": "No favicon configured"}

@api_router.get("/test-fast")
async def test_fast_endpoint():
    """Test endpoint to verify optimizations work"""
    return {"status": "fast", "message": "Optimizations working", "timestamp": datetime.utcnow().isoformat()}

# Initialize services (singletons)
alignment_service = AlignmentScoreService()
ai_coach_service = AiCoachMvpService()

# UPLOADS: simple chunked upload to local filesystem (for demo). In production, use cloud storage.
UPLOAD_ROOT = Path("/app/uploads")
TMP_DIR = UPLOAD_ROOT / "tmp"
FILES_DIR = UPLOAD_ROOT / "files"
for d in [UPLOAD_ROOT, TMP_DIR, FILES_DIR]:
    try:
        d.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

class UploadInitRequest(BaseModel):
    filename: str
    size: int
    parent_type: Optional[str] = None
    parent_id: Optional[str] = None

class UploadInitResponse(BaseModel):
    upload_id: str
    chunk_size: int
    total_chunks: int

@api_router.post("/uploads/initiate", response_model=UploadInitResponse)
async def initiate_upload(payload: UploadInitRequest, current_user: User = Depends(get_current_active_user)):
    try:
        upload_id = str(uuid.uuid4())
        meta_dir = TMP_DIR / upload_id
        meta_dir.mkdir(parents=True, exist_ok=True)
        # Write metadata
        (meta_dir / "meta.txt").write_text("\n".join([
            f"filename={payload.filename}",
            f"size={payload.size}",
            f"parent_type={payload.parent_type or ''}",
            f"parent_id={payload.parent_id or ''}",
            f"user_id={current_user.id}",
            f"created_at={datetime.utcnow().isoformat()}"
        ]), encoding="utf-8")
        # Recommend a 1MB chunk size
        chunk_size = 1024 * 1024
        total_chunks = max(1, (payload.size + chunk_size - 1) // chunk_size)
        return UploadInitResponse(upload_id=upload_id, chunk_size=chunk_size, total_chunks=total_chunks)
    except Exception as e:
        logger.error(f"initiate_upload failed: {e}")
        # Harden: return a 500 with message, client can retry
        raise HTTPException(status_code=500, detail="Failed to initiate upload")

@api_router.post("/uploads/chunk")
async def upload_chunk(
    upload_id: str = Form(...),
    index: int = Form(...),
    total_chunks: int = Form(...),
    chunk: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    try:
        meta_dir = TMP_DIR / upload_id
        if not meta_dir.exists():
            raise HTTPException(status_code=404, detail="Upload not found")
        part_path = meta_dir / f"part_{index:06d}"
        with open(part_path, "wb") as f:
            while True:
                data = await chunk.read(1024 * 1024)
                if not data:
                    break
                f.write(data)
        return {"received": True, "index": index, "total": total_chunks}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"upload_chunk failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload chunk")

class UploadCompleteResponse(BaseModel):
    upload_id: str
    file_url: str
    filename: str
    size: int

@api_router.post("/uploads/complete", response_model=UploadCompleteResponse)
async def complete_upload(upload_id: str = Form(...), current_user: User = Depends(get_current_active_user)):
    try:
        meta_dir = TMP_DIR / upload_id
        if not meta_dir.exists():
            raise HTTPException(status_code=404, detail="Upload not found")
        meta_txt = (meta_dir / "meta.txt").read_text(encoding="utf-8")
        meta = dict([line.split("=", 1) for line in meta_txt.splitlines() if "=" in line])
        filename = meta.get("filename", f"file-{upload_id}")
        # Assemble parts
        parts = sorted([p for p in meta_dir.iterdir() if p.name.startswith("part_")])
        final_dir = FILES_DIR / upload_id
        final_dir.mkdir(parents=True, exist_ok=True)
        final_path = final_dir / filename
        with open(final_path, "wb") as outfile:
            for part in parts:
                with open(part, "rb") as infile:
                    while True:
                        buf = infile.read(1024 * 1024)
                        if not buf:
                            break
                        outfile.write(buf)
        # Clean up parts (best-effort)
        for part in parts:
            try:
                part.unlink(missing_ok=True)
            except Exception:
                pass
        # Return URL for downloading/serving
        file_url = f"/api/uploads/file/{upload_id}/{filename}"
        size = os.path.getsize(final_path)
        return UploadCompleteResponse(upload_id=upload_id, file_url=file_url, filename=filename, size=size)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"complete_upload failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to complete upload")

@api_router.get("/uploads/file/{upload_id}/{filename}")
async def get_uploaded_file(upload_id: str, filename: str, current_user: User = Depends(get_current_active_user)):
    try:
        final_path = FILES_DIR / upload_id / filename
        if not final_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        return FileResponse(final_path)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"get_uploaded_file failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch file")

# Essential API endpoints for smoke testing
@api_router.get("/pillars")
async def get_pillars(current_user: User = Depends(get_current_active_user)):
    """Get user pillars"""
    try:
        service = SupabasePillarService()
        pillars = await service.get_user_pillars(str(current_user.id))
        return pillars
    except Exception as e:
        logger.error(f"Error getting pillars: {e}")
        raise HTTPException(status_code=500, detail="Failed to get pillars")

@api_router.get("/areas")
async def get_areas(current_user: User = Depends(get_current_active_user)):
    """Get user areas"""
    try:
        service = SupabaseAreaService()
        areas = await service.get_user_areas(str(current_user.id))
        return areas
    except Exception as e:
        logger.error(f"Error getting areas: {e}")
        raise HTTPException(status_code=500, detail="Failed to get areas")

@api_router.get("/projects")
async def get_projects(current_user: User = Depends(get_current_active_user)):
    """Get user projects"""
    try:
        service = SupabaseProjectService()
        projects = await service.get_user_projects(str(current_user.id))
        return projects
    except Exception as e:
        logger.error(f"Error getting projects: {e}")
        raise HTTPException(status_code=500, detail="Failed to get projects")

@api_router.get("/tasks")
async def get_tasks(
    project_id: Optional[str] = Query(default=None),
    q: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    priority: Optional[str] = Query(default=None),
    due_date: Optional[str] = Query(default=None),
    current_user: User = Depends(get_current_active_user)
):
    """Get user tasks with optional server-side filters"""
    try:
        task_service = TaskService()
        tasks = await task_service.get_user_tasks(
            str(current_user.id),
            project_id=project_id,
            q=q,
            status=status,
            priority=priority,
            due_date=due_date,
        )
        return tasks
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        raise HTTPException(status_code=500, detail="Failed to get tasks")

@api_router.get("/insights")
async def get_insights(
    date_range: Optional[str] = Query(default='all_time'),
    area_id: Optional[str] = Query(default=None),
    current_user: User = Depends(get_current_active_user)
):
    """Get user insights"""
    try:
        insights_service = InsightsService()
        insights = await insights_service.get_user_insights(str(current_user.id), date_range=date_range, area_id=area_id)
        return insights
    except Exception as e:
        logger.error(f"Error getting insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to get insights")

@api_router.get("/alignment/dashboard")
async def get_alignment_dashboard(current_user: User = Depends(get_current_active_user)):
    """Get alignment dashboard data"""
    try:
        return await alignment_service.get_alignment_dashboard(str(current_user.id))
    except Exception as e:
        logger.error(f"Error getting alignment dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to get alignment dashboard")

@api_router.get("/alignment-score")
async def get_alignment_score(current_user: User = Depends(get_current_active_user)):
    """Get alignment score (legacy endpoint)"""
    try:
        return await alignment_service.get_alignment_score(str(current_user.id))
    except Exception as e:
        logger.error(f"Error getting alignment score: {e}")
        raise HTTPException(status_code=500, detail="Failed to get alignment score")

@api_router.get("/journal")
async def get_journal(current_user: User = Depends(get_current_active_user)):
    """Get user journal entries"""
    try:
        journal_service = JournalService()
        entries = await journal_service.get_user_entries(str(current_user.id))
        return entries
    except Exception as e:
        logger.error(f"Error getting journal entries: {e}")
        raise HTTPException(status_code=500, detail="Failed to get journal entries")

# Mount the router last
app.include_router(api_router)
# Include auth router under /api prefix
app.include_router(auth_router, prefix="/api")