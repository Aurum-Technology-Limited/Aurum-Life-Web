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
from datetime import timedelta, datetime

# Import our models and Supabase services
from models import *
from supabase_services import (
    SupabaseUserService,
    SupabasePillarService, 
    SupabaseAreaService, 
    SupabaseProjectService,
    SupabaseTaskService,
    SupabaseDashboardService
)
from supabase_auth import get_current_active_user, verify_token
from supabase_auth_endpoints import auth_router
from hybrid_auth import get_current_active_user_hybrid

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create the main app
app = FastAPI(title="Aurum Life API - Supabase Only", version="2.0.0")

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

# Include authentication routes
app.include_router(auth_router)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Aurum Life API - Supabase Only", "version": "2.0.0", "status": "operational"}

# ================================
# PILLAR ENDPOINTS
# ================================

@api_router.post("/pillars", response_model=dict)
async def create_pillar(pillar_data: PillarCreate, current_user: User = Depends(get_current_active_user_hybrid)):
    """Create a new pillar"""
    try:
        result = await SupabasePillarService.create_pillar(str(current_user.id), pillar_data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating pillar: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.get("/pillars", response_model=List[dict])
async def get_pillars(
    include_areas: bool = Query(False, description="Include linked areas"),
    include_archived: bool = Query(False, description="Include archived pillars"),
    current_user: User = Depends(get_current_active_user_hybrid)
):
    """Get user's pillars"""
    try:
        pillars = await SupabasePillarService.get_user_pillars(
            str(current_user.id), 
            include_areas=include_areas, 
            include_archived=include_archived
        )
        return pillars
    except Exception as e:
        logger.error(f"Error getting pillars: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.put("/pillars/{pillar_id}", response_model=dict)
async def update_pillar(
    pillar_id: str, 
    pillar_data: PillarUpdate, 
    current_user: User = Depends(get_current_active_user_hybrid)
):
    """Update a pillar"""
    try:
        result = await SupabasePillarService.update_pillar(pillar_id, str(current_user.id), pillar_data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating pillar: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.delete("/pillars/{pillar_id}")
async def delete_pillar(pillar_id: str, current_user: User = Depends(get_current_active_user_hybrid)):
    """Delete a pillar"""
    try:
        success = await SupabasePillarService.delete_pillar(pillar_id, str(current_user.id))
        if not success:
            raise HTTPException(status_code=404, detail="Pillar not found")
        return {"message": "Pillar deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting pillar: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ================================
# AREA ENDPOINTS
# ================================

@api_router.post("/areas", response_model=dict)
async def create_area(area_data: AreaCreate, current_user: User = Depends(get_current_active_user_hybrid)):
    """Create a new area"""
    try:
        result = await SupabaseAreaService.create_area(str(current_user.id), area_data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating area: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.get("/areas", response_model=List[dict])
async def get_areas(
    include_projects: bool = Query(False, description="Include linked projects"),
    include_archived: bool = Query(False, description="Include archived areas"),
    current_user: User = Depends(get_current_active_user_hybrid)
):
    """Get user's areas"""
    try:
        areas = await SupabaseAreaService.get_user_areas(
            str(current_user.id), 
            include_projects=include_projects, 
            include_archived=include_archived
        )
        return areas
    except Exception as e:
        logger.error(f"Error getting areas: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.put("/areas/{area_id}", response_model=dict)
async def update_area(
    area_id: str, 
    area_data: AreaUpdate, 
    current_user: User = Depends(get_current_active_user_hybrid)
):
    """Update an area"""
    try:
        result = await SupabaseAreaService.update_area(area_id, str(current_user.id), area_data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating area: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.delete("/areas/{area_id}")
async def delete_area(area_id: str, current_user: User = Depends(get_current_active_user_hybrid)):
    """Delete an area"""
    try:
        success = await SupabaseAreaService.delete_area(area_id, str(current_user.id))
        if not success:
            raise HTTPException(status_code=404, detail="Area not found")
        return {"message": "Area deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting area: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ================================
# PROJECT ENDPOINTS
# ================================

@api_router.post("/projects", response_model=dict)
async def create_project(project_data: ProjectCreate, current_user: User = Depends(get_current_active_user)):
    """Create a new project"""
    try:
        result = await SupabaseProjectService.create_project(str(current_user.id), project_data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.get("/projects", response_model=List[dict])
async def get_projects(
    include_tasks: bool = Query(False, description="Include project tasks"),
    include_archived: bool = Query(False, description="Include archived projects"),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's projects"""
    try:
        projects = await SupabaseProjectService.get_user_projects(
            str(current_user.id), 
            include_tasks=include_tasks, 
            include_archived=include_archived
        )
        return projects
    except Exception as e:
        logger.error(f"Error getting projects: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.put("/projects/{project_id}", response_model=dict)
async def update_project(
    project_id: str, 
    project_data: ProjectUpdate, 
    current_user: User = Depends(get_current_active_user)
):
    """Update a project"""
    try:
        result = await SupabaseProjectService.update_project(project_id, str(current_user.id), project_data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating project: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.delete("/projects/{project_id}")
async def delete_project(project_id: str, current_user: User = Depends(get_current_active_user)):
    """Delete a project"""
    try:
        success = await SupabaseProjectService.delete_project(project_id, str(current_user.id))
        if not success:
            raise HTTPException(status_code=404, detail="Project not found")
        return {"message": "Project deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting project: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ================================
# TASK ENDPOINTS
# ================================

@api_router.post("/tasks", response_model=dict)
async def create_task(task_data: TaskCreate, current_user: User = Depends(get_current_active_user)):
    """Create a new task"""
    try:
        result = await SupabaseTaskService.create_task(str(current_user.id), task_data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.get("/tasks", response_model=List[dict])
async def get_tasks(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's tasks"""
    try:
        tasks = await SupabaseTaskService.get_user_tasks(
            str(current_user.id), 
            project_id=project_id, 
            completed=completed
        )
        return tasks
    except Exception as e:
        logger.error(f"Error getting tasks: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.put("/tasks/{task_id}", response_model=dict)
async def update_task(
    task_id: str, 
    task_data: TaskUpdate, 
    current_user: User = Depends(get_current_active_user)
):
    """Update a task"""
    try:
        result = await SupabaseTaskService.update_task(task_id, str(current_user.id), task_data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating task: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.delete("/tasks/{task_id}")
async def delete_task(task_id: str, current_user: User = Depends(get_current_active_user)):
    """Delete a task"""
    try:
        success = await SupabaseTaskService.delete_task(task_id, str(current_user.id))
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"message": "Task deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting task: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ================================
# DASHBOARD ENDPOINT
# ================================

@api_router.get("/dashboard", response_model=dict)
async def get_dashboard(current_user: User = Depends(get_current_active_user)):
    """Get dashboard data"""
    try:
        dashboard_data = await SupabaseDashboardService.get_dashboard_data(str(current_user.id))
        return dashboard_data
    except Exception as e:
        logger.error(f"Error getting dashboard data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ================================
# TODAY VIEW ENDPOINT
# ================================

@api_router.get("/today", response_model=dict)
async def get_today_view(current_user: User = Depends(get_current_active_user)):
    """Get today's tasks and priorities"""
    try:
        # Get today's incomplete tasks
        tasks = await SupabaseTaskService.get_user_tasks(str(current_user.id), completed=False)
        
        # Simple today view - can be enhanced later
        today_data = {
            'tasks': tasks[:10],  # Limit to 10 tasks
            'priorities': [],
            'recommendations': []
        }
        
        return today_data
    except Exception as e:
        logger.error(f"Error getting today view: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Include API router
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)