from fastapi import FastAPI, APIRouter, HTTPException, Query, Depends, status, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from pydantic import BaseModel
from pathlib import Path
import os
import logging
from typing import List, Optional
from datetime import datetime
import uuid

# Import our models and services
from supabase_client import supabase_manager
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
from supabase_auth import get_current_active_user
from supabase_auth_endpoints import auth_router
from analytics_service import AnalyticsService
from alignment_score_service import AlignmentScoreService
from ai_coach_mvp_service import AiCoachMvpService

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Secure dir for admin token persistence (kept for any future admin ops)
SECURE_DIR = Path('/app/secure')
try:
    SECURE_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass
ADMIN_TOKEN_FILE = SECURE_DIR / 'admin_token.txt'

def get_admin_token() -> str:
    token = os.environ.get('ADMIN_PURGE_TOKEN')
    if token:
        return token
    try:
        if ADMIN_TOKEN_FILE.exists():
            return ADMIN_TOKEN_FILE.read_text(encoding='utf-8').strip()
    except Exception:
        pass
    try:
        import secrets
        token = secrets.token_urlsafe(48)
        ADMIN_TOKEN_FILE.write_text(token, encoding='utf-8')
        return token
    except Exception:
        return 'admin-token-fallback'

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

# Health check endpoints
@api_router.get("/")
async def root():
    return {"message": "Aurum Life API is running", "version": "1.0.0"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/")
async def root():
    return {"message": "Aurum Life API", "version": "1.0.0", "status": "running"}

@app.get("/favicon.ico")
async def favicon():
    return {"message": "No favicon configured"}

@api_router.get("/test-fast")
async def test_fast_endpoint():
    return {"status": "fast", "message": "Optimizations working", "timestamp": datetime.utcnow().isoformat()}

# Initialize services (singletons)
alignment_service = AlignmentScoreService()
ai_coach_service = AiCoachMvpService()

# UPLOADS: simple chunked upload to local filesystem
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
        (meta_dir / "meta.txt").write_text("\n".join([
            f"filename={payload.filename}",
            f"size={payload.size}",
            f"parent_type={payload.parent_type or ''}",
            f"parent_id={payload.parent_id or ''}",
            f"user_id={current_user.id}",
            f"created_at={datetime.utcnow().isoformat()}"
        ]), encoding="utf-8")
        chunk_size = 1024 * 1024
        total_chunks = max(1, (payload.size + chunk_size - 1) // chunk_size)
        return UploadInitResponse(upload_id=upload_id, chunk_size=chunk_size, total_chunks=total_chunks)
    except Exception as e:
        logger.error(f"initiate_upload failed: {e}")
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
        for part in parts:
            try:
                part.unlink(missing_ok=True)
            except Exception:
                pass
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

# Essential API endpoints
@api_router.get("/pillars")
async def get_pillars(current_user: User = Depends(get_current_active_user)):
    try:
        service = SupabasePillarService()
        return await service.get_user_pillars(str(current_user.id))
    except Exception as e:
        logger.error(f"Error getting pillars: {e}")
        raise HTTPException(status_code=500, detail="Failed to get pillars")

@api_router.get("/areas")
async def get_areas(current_user: User = Depends(get_current_active_user)):
    try:
        service = SupabaseAreaService()
        return await service.get_user_areas(str(current_user.id))
    except Exception as e:
        logger.error(f"Error getting areas: {e}")
        raise HTTPException(status_code=500, detail="Failed to get areas")

@api_router.get("/projects")
async def get_projects(current_user: User = Depends(get_current_active_user)):
    try:
        service = SupabaseProjectService()
        return await service.get_user_projects(str(current_user.id))
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
    page: Optional[int] = Query(default=None, ge=1),
    limit: Optional[int] = Query(default=None, ge=1, le=200),
    return_meta: Optional[bool] = Query(default=False),
    current_user: User = Depends(get_current_active_user)
):
    try:
        task_service = TaskService()
        all_tasks = await task_service.get_user_tasks(
            str(current_user.id),
            project_id=project_id,
            q=q,
            status=status,
            priority=priority,
            due_date=due_date,
        )
        if not page or not limit:
            return all_tasks
        total = len(all_tasks)
        start = (page - 1) * limit
        end = start + limit
        page_items = all_tasks[start:end]
        if return_meta:
            return {"tasks": page_items, "total": total, "page": page, "limit": limit, "has_more": end < total}
        return page_items
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        raise HTTPException(status_code=500, detail="Failed to get tasks")

@api_router.get("/insights")
async def get_insights(
    date_range: Optional[str] = Query(default='all_time'),
    area_id: Optional[str] = Query(default=None),
    current_user: User = Depends(get_current_active_user)
):
    try:
        insights_service = InsightsService()
        return await insights_service.get_user_insights(str(current_user.id), date_range=date_range, area_id=area_id)
    except Exception as e:
        logger.error(f"Error getting insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to get insights")

@api_router.get("/alignment/dashboard")
async def get_alignment_dashboard(current_user: User = Depends(get_current_active_user)):
    try:
        return await alignment_service.get_alignment_dashboard(str(current_user.id))
    except Exception as e:
        logger.error(f"Error getting alignment dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to get alignment dashboard")

@api_router.get("/alignment-score")
async def get_alignment_score(current_user: User = Depends(get_current_active_user)):
    try:
        return await alignment_service.get_alignment_score(str(current_user.id))
    except Exception as e:
        logger.error(f"Error getting alignment score: {e}")
        raise HTTPException(status_code=500, detail="Failed to get alignment score")

@api_router.get("/journal")
async def get_journal(current_user: User = Depends(get_current_active_user)):
    try:
        journal_service = JournalService()
        return await journal_service.get_user_entries(str(current_user.id))
    except Exception as e:
        logger.error(f"Error getting journal entries: {e}")
        raise HTTPException(status_code=500, detail="Failed to get journal entries")

# Mount the router last
app.include_router(api_router)
app.include_router(auth_router, prefix="/api")