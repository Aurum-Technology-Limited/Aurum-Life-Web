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
from supabase_services import SupabasePillarService, SupabaseAreaService, SupabaseProjectService, SupabaseTaskService
from supabase_auth import get_current_active_user
from supabase_auth_endpoints import auth_router
from analytics_service import AnalyticsService
from alignment_score_service import AlignmentScoreService
from ai_coach_mvp_service import AiCoachMvpService
from hrm_endpoints import hrm_router

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

app = FastAPI(title="Aurum Life API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

# Upload endpoints omitted for brevity (unchanged)

# Essential API endpoints
@api_router.get("/pillars")
async def get_pillars(current_user: User = Depends(get_current_active_user)):
    try:
        service = SupabasePillarService()
        return await service.get_user_pillars(str(current_user.id))
    except Exception as e:
        logger.error(f"Error getting pillars: {e}")
        raise HTTPException(status_code=500, detail="Failed to get pillars")

@api_router.post("/pillars")
async def create_pillar(payload: PillarCreate, current_user: User = Depends(get_current_active_user)):
    try:
        result = await SupabasePillarService.create_pillar(str(current_user.id), payload)
        return result
    except Exception as e:
        logger.error(f"Error creating pillar: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/areas")
async def get_areas(current_user: User = Depends(get_current_active_user)):
    try:
        service = SupabaseAreaService()
        return await service.get_user_areas(str(current_user.id))
    except Exception as e:
        logger.error(f"Error getting areas: {e}")
        raise HTTPException(status_code=500, detail="Failed to get areas")

@api_router.post("/areas")
async def create_area(payload: AreaCreate, current_user: User = Depends(get_current_active_user)):
    try:
        result = await SupabaseAreaService.create_area(str(current_user.id), payload)
        return result
    except Exception as e:
        logger.error(f"Error creating area: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/projects")
async def get_projects(current_user: User = Depends(get_current_active_user)):
    try:
        service = SupabaseProjectService()
        return await service.get_user_projects(str(current_user.id))
    except Exception as e:
        logger.error(f"Error getting projects: {e}")
        raise HTTPException(status_code=500, detail="Failed to get projects")

@api_router.post("/projects")
async def create_project(payload: ProjectCreate, current_user: User = Depends(get_current_active_user)):
    try:
        result = await SupabaseProjectService.create_project(str(current_user.id), payload)
        return result
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        raise HTTPException(status_code=400, detail=str(e))

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

@api_router.post("/tasks")
async def create_task(payload: TaskCreate, current_user: User = Depends(get_current_active_user)):
    try:
        result = await SupabaseTaskService.create_task(str(current_user.id), payload)
        return result
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=400, detail=str(e))

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

@api_router.get("/journal")
async def get_journal(current_user: User = Depends(get_current_active_user)):
    try:
        journal_service = JournalService()
        return await journal_service.get_user_entries(str(current_user.id))
    except Exception as e:
        logger.error(f"Error getting journal entries: {e}")
        raise HTTPException(status_code=500, detail="Failed to get journal entries")

app.include_router(api_router)
app.include_router(auth_router, prefix="/api")
app.include_router(hrm_router)