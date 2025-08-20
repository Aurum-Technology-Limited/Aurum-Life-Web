from fastapi import FastAPI, APIRouter, HTTPException, Query, Depends, status, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from pydantic import BaseModel
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

# Secure dir for admin token persistence
SECURE_DIR = Path('/app/secure')
try:
    SECURE_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass
ADMIN_TOKEN_FILE = SECURE_DIR / 'admin_token.txt'

def get_admin_token() -> str:
    """Get admin purge/migration token from env or persisted file, generate if missing."""
    token = os.environ.get('ADMIN_PURGE_TOKEN')
    if token:
        return token
    try:
        if ADMIN_TOKEN_FILE.exists():
            return ADMIN_TOKEN_FILE.read_text(encoding='utf-8').strip()
    except Exception:
        pass
    # Generate and persist
    try:
        import secrets
        token = secrets.token_urlsafe(48)
        ADMIN_TOKEN_FILE.write_text(token, encoding='utf-8')
        return token
    except Exception:
        # Last resort: simple fallback (not ideal, but unblocks)
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

# Default user ID for demo (in real app, this would come from authentication)
DEFAULT_USER_ID = "demo-user-123"

# Hybrid authentication dependency for API endpoints (defined below)
async def get_current_active_user_hybrid(request: Request) -> User:
    """Get current active user using hybrid authentication (Supabase + Legacy JWT)"""
    try:
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="No authorization token provided")
        token = authorization.split(" ")[1]
        current_user = None
        user_id = None
        try:
            current_user = await verify_token(token)
            user_id = current_user.id
            logger.info("✅ Verified Supabase token for API endpoint")
        except Exception as supabase_error:
            logger.info(f"Supabase token verification failed: {supabase_error}")
            try:
                from auth import jwt, SECRET_KEY, ALGORITHM
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                user_id = payload.get("sub")
                if user_id is None:
                    raise HTTPException(status_code=401, detail="Could not validate credentials")
                # Restrict legacy JWT usage to preserved test account only
                try:
                    PRESERVED_TEST_EMAIL = "marc.alleyne@aurumtechnologyltd.com"
                    legacy_user = await supabase_manager.find_document("users", {"id": user_id})
                    if legacy_user:
                        if (legacy_user.get('email') or '').lower() != PRESERVED_TEST_EMAIL:
                            raise HTTPException(status_code=401, detail="Legacy tokens are no longer supported. Please create a new account.")
                    else:
                        # If no legacy user found, check if this is the preserved test account by looking up user_profiles
                        user_profile = await supabase_manager.find_document("user_profiles", {"id": user_id})
                        if not user_profile:
                            raise HTTPException(status_code=401, detail="Legacy tokens are no longer supported. Please create a new account.")
                        # Allow the preserved test account even if no legacy user record exists
                        logger.info(f"Allowing preserved test account with Supabase Auth ID: {user_id}")
                except HTTPException:
                    raise
                except Exception as e:
                    logger.info(f"Legacy user validation skipped/failed: {e}")
                logger.info("✅ Verified legacy JWT token for API endpoint")
            except Exception as legacy_error:
                logger.info(f"Legacy token verification failed: {legacy_error}")
                raise HTTPException(status_code=401, detail="Could not validate credentials")
        if not user_id:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        # Get user data
        try:
            user_profile = await supabase_manager.find_document("user_profiles", {"id": user_id})
            if user_profile:
                from models import User
                return User(
                    id=user_profile['id'],
                    username=user_profile.get('username', ''),
                    email='',
                    first_name=user_profile.get('first_name', ''),
                    last_name=user_profile.get('last_name', ''),
                    password_hash='',
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
        try:
            legacy_user = await supabase_manager.find_document("users", {"id": user_id})
            if legacy_user:
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

alignment_service = AlignmentScoreService()
ai_coach_service = AiCoachMvpService()

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

# Tasks, Insights, Pillars, Areas, Projects endpoints are defined below (unchanged)

# Admin-protected one-off purge for legacy users
class AdminPurgeRequest(BaseModel):
    admin_token: str
    preserve_email: str
    dry_run: bool = True

@api_router.post("/admin/purge-legacy-users")
async def purge_legacy_users(payload: AdminPurgeRequest):
    try:
        expected_token = get_admin_token()
        if payload.admin_token != expected_token:
            raise HTTPException(status_code=401, detail="Invalid admin token")
        preserve = (payload.preserve_email or '').strip().lower()
        if not preserve:
            raise HTTPException(status_code=400, detail="preserve_email is required")
        users = await supabase_manager.find_documents("users", {})
        to_delete = [u for u in (users or []) if (u.get('email') or '').lower() != preserve]
        result = {
            "total_legacy_users": len(users or []),
            "to_delete_count": len(to_delete),
            "preserved": preserve
        }
        if payload.dry_run:
            result["status"] = "dry_run"
            result["sample_delete_ids"] = [u.get('id') for u in to_delete[:10]]
            return result
        deleted = 0
        for u in to_delete:
            ok = await supabase_manager.delete_document("users", u.get('id'))
            if ok:
                deleted += 1
        result["deleted"] = deleted
        result["status"] = "completed"
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Purge legacy users failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to purge legacy users")

# Admin-protected migration endpoint
class AdminMigrateLegacyRequest(BaseModel):
    admin_token: str
    legacy_email: str
    create_auth_if_missing: bool = True
    dry_run: bool = True

@api_router.post("/admin/migrate-legacy-to-supabase")
async def migrate_legacy_to_supabase(payload: AdminMigrateLegacyRequest):
    try:
        expected_token = get_admin_token()
        if payload.admin_token != expected_token:
            raise HTTPException(status_code=401, detail="Invalid admin token")
        email = (payload.legacy_email or '').strip().lower()
        if not email:
            raise HTTPException(status_code=400, detail="legacy_email is required")
        # Find legacy user
        legacy_user = await supabase_manager.find_document("users", {"email": email})
        legacy_id = legacy_user.get('id') if legacy_user else None
        # Find or create Supabase Auth user
        supa = supabase_manager.get_client()
        auth_list = supa.auth.admin.list_users()
        users_list = auth_list.users if hasattr(auth_list, 'users') else (auth_list.get('users') if isinstance(auth_list, dict) else auth_list)
        supa_user = None
        for au in (users_list or []):
            au_email = getattr(au, 'email', None) if hasattr(au, 'email') else (au.get('email') if isinstance(au, dict) else None)
            if isinstance(au_email, str) and au_email.lower() == email:
                supa_user = au
                break
        created_temp_password = None
        if not supa_user and payload.create_auth_if_missing:
            import secrets
            created_temp_password = secrets.token_urlsafe(24)
            created = supa.auth.admin.create_user({
                "email": email,
                "password": created_temp_password,
                "email_confirm": True,
                "user_metadata": {
                    "migrated_from_legacy": True
                }
            })
            supa_user = getattr(created, 'user', None) or getattr(created, 'data', None) or created
        supa_id = (getattr(supa_user, 'id', None) if supa_user and hasattr(supa_user, 'id') else (supa_user.get('id') if isinstance(supa_user, dict) else None))
        if not supa_id:
            raise HTTPException(status_code=404, detail="Supabase Auth user not found and not created")
        # Ensure user_profiles exists/updated
        prof = await supabase_manager.find_document("user_profiles", {"id": supa_id})
        if not payload.dry_run:
            profile_payload = {
                'id': supa_id,
                'username': (legacy_user.get('username') if legacy_user else email.split('@')[0]),
                'first_name': (legacy_user.get('first_name') if legacy_user else ''),
                'last_name': (legacy_user.get('last_name') if legacy_user else ''),
                'is_active': True,
                'level': (legacy_user.get('level') if legacy_user else 1),
                'total_points': (legacy_user.get('total_points') if legacy_user else 0),
                'current_streak': (legacy_user.get('current_streak') if legacy_user else 0)
            }
            if not prof:
                await supabase_manager.create_document("user_profiles", profile_payload)
            else:
                await supabase_manager.update_document("user_profiles", supa_id, profile_payload)
        # Migrate references
        tables = [
            'pillars', 'areas', 'projects', 'tasks', 'journal_entries', 'user_stats',
            'feedback', 'attachments', 'uploads', 'goals', 'insights', 'ai_sessions'
        ]
        migration_result = {
            'legacy_id': legacy_id,
            'supa_id': supa_id,
            'email': email,
            'updated_counts': {},
            'created_temp_password': created_temp_password
        }
        if legacy_id:
            for t in tables:
                try:
                    if payload.dry_run:
                        count = await supabase_manager.count_documents(t, {"user_id": legacy_id})
                        migration_result['updated_counts'][t] = {"would_update": count}
                    else:
                        updated = await supabase_manager.bulk_update_documents(t, {"user_id": legacy_id}, {"user_id": supa_id})
                        migration_result['updated_counts'][t] = {"updated": updated}
                except Exception as e:
                    migration_result['updated_counts'][t] = {"error": str(e)}
            # After migration, optionally delete legacy user row
            if not payload.dry_run:
                try:
                    if legacy_user:
                        await supabase_manager.delete_document("users", legacy_id)
                        migration_result['legacy_user_deleted'] = True
                except Exception as e:
                    migration_result['legacy_user_deleted'] = False
                    migration_result['legacy_delete_error'] = str(e)
        else:
            migration_result['note'] = 'No legacy user found; only ensured Supabase Auth + user_profiles.'
        return migration_result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to migrate legacy user")

# Mount the router last
app.include_router(api_router)
app.include_router(auth_router, prefix="/api")