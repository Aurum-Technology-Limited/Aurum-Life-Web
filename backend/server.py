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

# Import our models and Supabase services
from models import *
from supabase_services import (
    SupabaseUserService,
    SupabasePillarService, 
    SupabaseAreaService, 
    SupabaseProjectService,
    SupabaseTaskService,
    SupabaseDashboardService,
    SupabaseInsightsService
)
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
from models import (
    DailyReflectionCreate,
    DailyReflectionResponse,
    ProjectDecompositionRequest,
    ProjectDecompositionResponse,
    TaskWhyStatementResponse
)

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
# AI COACH MVP FEATURES ENDPOINTS
# ================================

# Initialize AI Coach MVP service
ai_coach_mvp = AiCoachMvpService()

# Feature 1: Contextual "Why" Statements
@api_router.get("/ai/task-why-statements", response_model=TaskWhyStatementResponse)
async def get_task_why_statements(
    task_ids: Optional[str] = None,
    current_user: User = Depends(get_current_active_user_hybrid)
):
    """
    Get contextual why statements for tasks explaining their vertical alignment
    
    Query Parameters:
    - task_ids: Optional comma-separated list of task IDs (if not provided, uses recent incomplete tasks)
    """
    try:
        user_id = current_user.id
        
        # Parse task_ids if provided
        parsed_task_ids = None
        if task_ids:
            parsed_task_ids = [tid.strip() for tid in task_ids.split(',') if tid.strip()]
        
        why_statements = await ai_coach_mvp.generate_task_why_statements(user_id, parsed_task_ids)
        return why_statements
        
    except Exception as e:
        logger.error(f"Error getting task why statements: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate task context")

# Feature 2: Lean Goal Decomposition Assistance
@api_router.post("/ai/decompose-project", response_model=ProjectDecompositionResponse)
async def decompose_project(
    request: ProjectDecompositionRequest,
    current_user: User = Depends(get_current_active_user_hybrid)
):
    """
    Get suggested tasks for a new project to help with the blank slate problem
    
    Body:
    - project_name: Name of the project
    - project_description: Optional description 
    - template_type: Type of project (learning, health, career, personal, work, general)
    """
    try:
        user_id = current_user.id
        suggestions = await ai_coach_mvp.suggest_project_tasks(user_id, request)
        return suggestions
        
    except Exception as e:
        logger.error(f"Error decomposing project: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate project suggestions")

@api_router.post("/ai/create-suggested-tasks")
async def create_suggested_tasks(
    project_id: str,
    suggested_tasks: List[Dict[str, Any]],
    current_user: User = Depends(get_current_active_user_hybrid)
):
    """
    Create actual tasks from suggested tasks for a project
    
    Body:
    - project_id: ID of the project to add tasks to
    - suggested_tasks: List of suggested task dictionaries
    """
    try:
        user_id = current_user.id
        created_tasks = await ai_coach_mvp.create_tasks_from_suggestions(
            user_id, project_id, suggested_tasks
        )
        
        return {
            "success": True,
            "created_tasks": created_tasks,
            "count": len(created_tasks)
        }
        
    except Exception as e:
        logger.error(f"Error creating suggested tasks: {e}")
        raise HTTPException(status_code=500, detail="Failed to create suggested tasks")

# Feature 3: Daily Reflection & Progress Prompt
@api_router.post("/ai/daily-reflection", response_model=DailyReflectionResponse)
async def create_daily_reflection(
    reflection_data: DailyReflectionCreate,
    current_user: User = Depends(get_current_active_user_hybrid)
):
    """
    Create or update a daily reflection entry
    
    Body:
    - reflection_text: Main reflection text (required)
    - completion_score: Optional 1-10 completion score
    - mood: Optional mood description
    - biggest_accomplishment: Optional biggest accomplishment text
    - challenges_faced: Optional challenges text
    - tomorrow_focus: Optional tomorrow focus text
    - reflection_date: Optional date (defaults to today)
    """
    try:
        user_id = current_user.id
        reflection = await ai_coach_mvp.create_daily_reflection(user_id, reflection_data)
        return reflection
        
    except Exception as e:
        logger.error(f"Error creating daily reflection: {e}")
        raise HTTPException(status_code=500, detail="Failed to create daily reflection")

@api_router.get("/ai/daily-reflections")
async def get_daily_reflections(
    days: int = 30,
    current_user: User = Depends(get_current_active_user_hybrid)
):
    """
    Get user's recent daily reflections
    
    Query Parameters:
    - days: Number of days to look back (default: 30)
    """
    try:
        user_id = current_user.id
        reflections = await ai_coach_mvp.get_user_reflections(user_id, days)
        return {
            "reflections": reflections,
            "count": len(reflections)
        }
        
    except Exception as e:
        logger.error(f"Error getting daily reflections: {e}")
        raise HTTPException(status_code=500, detail="Failed to get daily reflections")

@api_router.get("/ai/daily-streak")
async def get_daily_streak(
    current_user: User = Depends(get_current_active_user_hybrid)
):
    """Get user's current daily streak"""
    try:
        user_id = current_user.id
        streak = await ai_coach_mvp.get_user_streak(user_id)
        return {
            "daily_streak": streak,
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Error getting daily streak: {e}")
        raise HTTPException(status_code=500, detail="Failed to get daily streak")

@api_router.get("/ai/should-show-daily-prompt")
async def should_show_daily_prompt(
    current_user: dict = Depends(get_current_active_user_hybrid)
):
    """Check if daily reflection prompt should be shown"""
    try:
        user_id = current_user.id
        should_show = await ai_coach_mvp.should_show_daily_prompt(user_id)
        return {
            "should_show_prompt": should_show,
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Error checking daily prompt status: {e}")
        raise HTTPException(status_code=500, detail="Failed to check prompt status")

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
async def create_project(project_data: ProjectCreate, current_user: User = Depends(get_current_active_user_hybrid)):
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
    current_user: User = Depends(get_current_active_user_hybrid)
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
    current_user: User = Depends(get_current_active_user_hybrid)
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
async def delete_project(project_id: str, current_user: User = Depends(get_current_active_user_hybrid)):
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
async def create_task(task_data: TaskCreate, current_user: User = Depends(get_current_active_user_hybrid)):
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
    current_user: User = Depends(get_current_active_user_hybrid)
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
    current_user: User = Depends(get_current_active_user_hybrid)
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
async def delete_task(task_id: str, current_user: User = Depends(get_current_active_user_hybrid)):
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
async def get_dashboard(current_user: User = Depends(get_current_active_user_hybrid)):
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
async def get_today_view(current_user: User = Depends(get_current_active_user_hybrid)):
    """Get today's tasks and priorities"""
    try:
        # Get today's incomplete tasks
        tasks = await SupabaseTaskService.get_user_tasks(str(current_user.id), completed=False)
        
        # Simple today view - can be enhanced later
        today_data = {
            'tasks': tasks[:10],  # Limit to 10 tasks
            'priorities': [],
            'recommendations': [],
            'completed_tasks': len([t for t in tasks if t.get('completed', False)]),
            'total_tasks': len(tasks)
        }
        
        return today_data
    except Exception as e:
        logger.error(f"Error getting today view: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.get("/today/available-tasks")
async def get_available_tasks(current_user: User = Depends(get_current_active_user_hybrid)):
    """Get available tasks that can be added to today's list"""
    try:
        # Get all user tasks
        all_tasks = await SupabaseTaskService.get_user_tasks(str(current_user.id))
        
        # Filter out completed tasks and return available ones
        available_tasks = [task for task in all_tasks if not task.get('completed', False)]
        
        return available_tasks
    except Exception as e:
        logger.error(f"Error getting available tasks: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.post("/today/tasks/{task_id}")
async def add_task_to_today(
    task_id: str,
    current_user: User = Depends(get_current_active_user_hybrid)
):
    """Add a task to today's list"""
    try:
        # For now, just return success - can be enhanced with actual today list management
        return {"message": "Task added to today's list", "task_id": task_id}
    except Exception as e:
        logger.error(f"Error adding task to today: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.delete("/today/tasks/{task_id}")
async def remove_task_from_today(
    task_id: str,
    current_user: User = Depends(get_current_active_user_hybrid)
):
    """Remove a task from today's list"""
    try:
        # For now, just return success - can be enhanced with actual today list management
        return {"message": "Task removed from today's list", "task_id": task_id}
    except Exception as e:
        logger.error(f"Error removing task from today: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.put("/today/reorder")
async def reorder_daily_tasks(
    task_data: dict,
    current_user: User = Depends(get_current_active_user_hybrid)
):
    """Reorder tasks in today's list"""
    try:
        # For now, just return success - can be enhanced with actual reordering
        task_ids = task_data.get('task_ids', [])
        return {"message": "Tasks reordered successfully", "task_ids": task_ids}
    except Exception as e:
        logger.error(f"Error reordering tasks: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ================================
# PROJECT TEMPLATES ENDPOINTS
# ================================

@api_router.get("/project-templates")
async def get_project_templates(current_user: User = Depends(get_current_active_user_hybrid)):
    """Get all project templates for the user"""
    try:
        # For now, return mock templates - can be enhanced with actual database storage
        mock_templates = [
            {
                "id": "template-1",
                "name": "Website Development",
                "description": "Complete website development project with all necessary tasks",
                "category": "Development",
                "tasks": [
                    {"name": "Requirements Gathering", "description": "Collect and document requirements", "priority": "high", "estimated_duration": 120},
                    {"name": "Design Mockups", "description": "Create visual designs", "priority": "high", "estimated_duration": 240},
                    {"name": "Frontend Development", "description": "Build user interface", "priority": "medium", "estimated_duration": 480},
                    {"name": "Backend Development", "description": "Build server-side logic", "priority": "medium", "estimated_duration": 360},
                    {"name": "Testing", "description": "Test all functionality", "priority": "high", "estimated_duration": 120},
                    {"name": "Deployment", "description": "Deploy to production", "priority": "medium", "estimated_duration": 60}
                ],
                "created_at": "2024-01-15T10:00:00Z",
                "updated_at": "2024-01-15T10:00:00Z"
            },
            {
                "id": "template-2", 
                "name": "Marketing Campaign",
                "description": "Comprehensive marketing campaign planning and execution",
                "category": "Marketing",
                "tasks": [
                    {"name": "Market Research", "description": "Research target audience and competitors", "priority": "high", "estimated_duration": 180},
                    {"name": "Strategy Planning", "description": "Develop marketing strategy", "priority": "high", "estimated_duration": 120},
                    {"name": "Content Creation", "description": "Create marketing materials", "priority": "medium", "estimated_duration": 300},
                    {"name": "Campaign Launch", "description": "Execute marketing campaign", "priority": "high", "estimated_duration": 60},
                    {"name": "Performance Analysis", "description": "Analyze campaign results", "priority": "medium", "estimated_duration": 90}
                ],
                "created_at": "2024-01-15T10:00:00Z",
                "updated_at": "2024-01-15T10:00:00Z"
            },
            {
                "id": "template-3",
                "name": "Product Launch",
                "description": "Complete product launch process from planning to post-launch analysis",
                "category": "Product",
                "tasks": [
                    {"name": "Product Planning", "description": "Define product specifications and features", "priority": "high", "estimated_duration": 240},
                    {"name": "Development", "description": "Build the product", "priority": "high", "estimated_duration": 720},
                    {"name": "Quality Assurance", "description": "Test product thoroughly", "priority": "high", "estimated_duration": 180},
                    {"name": "Marketing Preparation", "description": "Prepare marketing materials", "priority": "medium", "estimated_duration": 120},
                    {"name": "Launch Event", "description": "Execute product launch", "priority": "high", "estimated_duration": 90},
                    {"name": "Post-Launch Support", "description": "Provide customer support and fixes", "priority": "medium", "estimated_duration": 160}
                ],
                "created_at": "2024-01-15T10:00:00Z",
                "updated_at": "2024-01-15T10:00:00Z"
            }
        ]
        
        return mock_templates
    except Exception as e:
        logger.error(f"Error getting project templates: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.get("/project-templates/{template_id}")
async def get_project_template(
    template_id: str,
    current_user: User = Depends(get_current_active_user_hybrid)
):
    """Get a specific project template"""
    try:
        # Mock template data - can be enhanced with actual database lookup
        if template_id == "template-1":
            template = {
                "id": "template-1",
                "name": "Website Development",
                "description": "Complete website development project with all necessary tasks",
                "category": "Development",
                "tasks": [
                    {"name": "Requirements Gathering", "description": "Collect and document requirements", "priority": "high", "estimated_duration": 120},
                    {"name": "Design Mockups", "description": "Create visual designs", "priority": "high", "estimated_duration": 240},
                    {"name": "Frontend Development", "description": "Build user interface", "priority": "medium", "estimated_duration": 480},
                    {"name": "Backend Development", "description": "Build server-side logic", "priority": "medium", "estimated_duration": 360},
                    {"name": "Testing", "description": "Test all functionality", "priority": "high", "estimated_duration": 120},
                    {"name": "Deployment", "description": "Deploy to production", "priority": "medium", "estimated_duration": 60}
                ]
            }
            return template
        else:
            raise HTTPException(status_code=404, detail="Template not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project template: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.post("/project-templates")
async def create_project_template(
    template_data: dict,
    current_user: User = Depends(get_current_active_user_hybrid)
):
    """Create a new project template"""
    try:
        # For now, return success with generated ID - can be enhanced with actual database storage
        template_id = f"template-{len(template_data.get('name', ''))}-{hash(template_data.get('name', '')) % 10000}"
        
        response = {
            "id": template_id,
            "message": "Template created successfully",
            **template_data,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        return response
    except Exception as e:
        logger.error(f"Error creating project template: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.put("/project-templates/{template_id}")
async def update_project_template(
    template_id: str,
    template_data: dict,
    current_user: User = Depends(get_current_active_user_hybrid)
):
    """Update a project template"""
    try:
        # For now, return success - can be enhanced with actual database update
        response = {
            "id": template_id,
            "message": "Template updated successfully",
            **template_data,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        return response
    except Exception as e:
        logger.error(f"Error updating project template: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.delete("/project-templates/{template_id}")
async def delete_project_template(
    template_id: str,
    current_user: User = Depends(get_current_active_user_hybrid)
):
    """Delete a project template"""
    try:
        # For now, return success - can be enhanced with actual database deletion
        return {"message": "Template deleted successfully", "template_id": template_id}
    except Exception as e:
        logger.error(f"Error deleting project template: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.post("/project-templates/{template_id}/use")
async def use_project_template(
    template_id: str,
    project_data: dict,
    current_user: User = Depends(get_current_active_user_hybrid)
):
    """Create a project from a template"""
    try:
        # For now, return success with project creation - can be enhanced with actual project and task creation
        project_id = f"project-from-{template_id}-{hash(project_data.get('name', '')) % 10000}"
        
        response = {
            "project_id": project_id,
            "message": "Project created from template successfully",
            "template_id": template_id,
            **project_data,
            "created_at": datetime.utcnow().isoformat()
        }
        
        return response
    except Exception as e:
        logger.error(f"Error using project template: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ================================
# JOURNAL ENDPOINTS
# ================================

@api_router.get("/journal")
async def get_journal_entries(
    skip: int = 0,
    limit: int = 20,
    mood_filter: Optional[str] = None,
    tag_filter: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: User = Depends(get_current_active_user_hybrid)
):
    """Get journal entries for the user"""
    try:
        # Mock journal entries data
        mock_entries = [
            {
                "id": "entry-1",
                "title": "Productive Day",
                "content": "Had a great day working on the new project. Made significant progress on the frontend components.",
                "mood": "happy",
                "tags": ["work", "productivity", "frontend"],
                "date": "2024-01-15T18:30:00Z",
                "created_at": "2024-01-15T18:30:00Z",
                "updated_at": "2024-01-15T18:30:00Z"
            },
            {
                "id": "entry-2", 
                "title": "Learning New Things",
                "content": "Spent time learning React optimization techniques. React.memo is really powerful for preventing unnecessary re-renders.",
                "mood": "excited",
                "tags": ["learning", "react", "optimization"],
                "date": "2024-01-14T20:15:00Z",
                "created_at": "2024-01-14T20:15:00Z",
                "updated_at": "2024-01-14T20:15:00Z"
            }
        ]
        
        # Apply filters if provided
        filtered_entries = mock_entries
        if mood_filter:
            filtered_entries = [e for e in filtered_entries if e['mood'] == mood_filter]
        
        # Apply pagination
        paginated_entries = filtered_entries[skip:skip+limit]
        
        return {
            "entries": paginated_entries,
            "total": len(filtered_entries),
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error getting journal entries: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.post("/journal")
async def create_journal_entry(
    entry_data: dict,
    current_user: User = Depends(get_current_active_user_hybrid)
):
    """Create a new journal entry"""
    try:
        entry_id = f"entry-{hash(entry_data.get('title', '')) % 10000}"
        
        response = {
            "id": entry_id,
            "message": "Journal entry created successfully",
            **entry_data,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        return response
    except Exception as e:
        logger.error(f"Error creating journal entry: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.put("/journal/{entry_id}")
async def update_journal_entry(
    entry_id: str,
    entry_data: dict,
    current_user: User = Depends(get_current_active_user_hybrid)
):
    """Update a journal entry"""
    try:
        response = {
            "id": entry_id,
            "message": "Journal entry updated successfully",
            **entry_data,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        return response
    except Exception as e:
        logger.error(f"Error updating journal entry: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.delete("/journal/{entry_id}")
async def delete_journal_entry(
    entry_id: str,
    current_user: User = Depends(get_current_active_user_hybrid)
):
    """Delete a journal entry"""
    try:
        return {"message": "Journal entry deleted successfully", "entry_id": entry_id}
    except Exception as e:
        logger.error(f"Error deleting journal entry: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.get("/journal/search")
async def search_journal_entries(
    q: str,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user_hybrid)
):
    """Search journal entries"""
    try:
        # Mock search results
        mock_results = [
            {
                "id": "entry-1",
                "title": "Productive Day",
                "content": "Had a great day working on the new project...",
                "mood": "happy",
                "date": "2024-01-15T18:30:00Z",
                "relevance_score": 0.95
            }
        ]
        
        return {
            "results": mock_results,
            "query": q,
            "total": len(mock_results)
        }
    except Exception as e:
        logger.error(f"Error searching journal entries: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.get("/journal/insights")
async def get_journal_insights(current_user: User = Depends(get_current_active_user_hybrid)):
    """Get journal insights and analytics"""
    try:
        insights = {
            "total_entries": 47,
            "entries_this_month": 12,
            "most_common_mood": "happy",
            "mood_distribution": {
                "happy": 20,
                "neutral": 15,
                "excited": 8,
                "sad": 4
            },
            "writing_streak": 7,
            "popular_tags": [
                {"tag": "work", "count": 23},
                {"tag": "learning", "count": 15},
                {"tag": "personal", "count": 12}
            ],
            "monthly_stats": [
                {"month": "Jan 2024", "entries": 12, "avg_mood": "happy"},
                {"month": "Dec 2023", "entries": 18, "avg_mood": "neutral"}
            ]
        }
        
        return insights
    except Exception as e:
        logger.error(f"Error getting journal insights: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.get("/journal/on-this-day")
async def get_journal_on_this_day(
    date: Optional[str] = None,
    current_user: User = Depends(get_current_active_user_hybrid)
):
    """Get journal entries from this day in previous years"""
    try:
        # Mock historical entries
        historical_entries = [
            {
                "id": "entry-historical-1",
                "title": "One Year Ago Today",
                "content": "Started learning React for the first time. Had no idea how powerful it would become in my toolkit.",
                "date": "2023-01-15T18:30:00Z",
                "year": 2023
            }
        ]
        
        return {
            "entries": historical_entries,
            "date": date or datetime.utcnow().strftime("%Y-%m-%d")
        }
    except Exception as e:
        logger.error(f"Error getting journal on this day: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Journal Templates
@api_router.get("/journal/templates")
async def get_journal_templates(current_user: User = Depends(get_current_active_user_hybrid)):
    """Get journal templates"""
    try:
        templates = [
            {
                "id": "template-daily",
                "name": "Daily Reflection", 
                "description": "Template for daily reflection and goal tracking",
                "structure": {
                    "sections": [
                        {"name": "Today I accomplished", "type": "text"},
                        {"name": "Challenges I faced", "type": "text"},
                        {"name": "Tomorrow I will", "type": "text"},
                        {"name": "Mood", "type": "select", "options": ["happy", "neutral", "sad", "excited"]}
                    ]
                },
                "created_at": "2024-01-15T10:00:00Z"
            },
            {
                "id": "template-gratitude",
                "name": "Gratitude Journal",
                "description": "Focus on gratitude and positive experiences",
                "structure": {
                    "sections": [
                        {"name": "Three things I'm grateful for", "type": "list"},
                        {"name": "Best part of my day", "type": "text"},
                        {"name": "Acts of kindness I witnessed", "type": "text"}
                    ]
                },
                "created_at": "2024-01-15T10:00:00Z"
            }
        ]
        
        return templates
    except Exception as e:
        logger.error(f"Error getting journal templates: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.get("/journal/templates/{template_id}")
async def get_journal_template(
    template_id: str,
    current_user: User = Depends(get_current_active_user_hybrid)
):
    """Get a specific journal template"""
    try:
        if template_id == "template-daily":
            template = {
                "id": "template-daily",
                "name": "Daily Reflection",
                "description": "Template for daily reflection and goal tracking",
                "structure": {
                    "sections": [
                        {"name": "Today I accomplished", "type": "text"},
                        {"name": "Challenges I faced", "type": "text"},
                        {"name": "Tomorrow I will", "type": "text"},
                        {"name": "Mood", "type": "select", "options": ["happy", "neutral", "sad", "excited"]}
                    ]
                }
            }
            return template
        else:
            raise HTTPException(status_code=404, detail="Template not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting journal template: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.post("/journal/templates")
async def create_journal_template(
    template_data: dict,
    current_user: User = Depends(get_current_active_user_hybrid)
):
    """Create a new journal template"""
    try:
        template_id = f"template-{hash(template_data.get('name', '')) % 10000}"
        
        response = {
            "id": template_id,
            "message": "Journal template created successfully",
            **template_data,
            "created_at": datetime.utcnow().isoformat()
        }
        
        return response
    except Exception as e:
        logger.error(f"Error creating journal template: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.put("/journal/templates/{template_id}")
async def update_journal_template(
    template_id: str,
    template_data: dict,
    current_user: User = Depends(get_current_active_user_hybrid)
):
    """Update a journal template"""
    try:
        response = {
            "id": template_id,
            "message": "Journal template updated successfully",
            **template_data,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        return response
    except Exception as e:
        logger.error(f"Error updating journal template: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.delete("/journal/templates/{template_id}")
async def delete_journal_template(
    template_id: str,
    current_user: User = Depends(get_current_active_user_hybrid)
):
    """Delete a journal template"""
    try:
        return {"message": "Journal template deleted successfully", "template_id": template_id}
    except Exception as e:
        logger.error(f"Error deleting journal template: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ================================
# INSIGHTS ENDPOINTS
# ================================

@api_router.get("/insights")
async def get_insights(
    date_range: str = "all_time",
    area_id: Optional[str] = None,
    current_user: User = Depends(get_current_active_user_hybrid)
):
    """Get comprehensive insights and analytics with real user data"""
    try:
        insights = await SupabaseInsightsService.get_comprehensive_insights(
            user_id=str(current_user.id),
            date_range=date_range
        )
        return insights
    except Exception as e:
        logger.error(f"Error getting insights: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.get("/insights/areas/{area_id}")
async def get_area_insights(
    area_id: str,
    date_range: str = "all_time",
    current_user: User = Depends(get_current_active_user_hybrid)
):
    """Get insights for a specific area"""
    try:
        area_insights = {
            "area_id": area_id,
            "tasks_completed": 45,
            "projects_completed": 8,
            "completion_rate": 87.5,
            "time_spent": 120, # hours
            "productivity_score": 4.2,
            "recent_activity": [
                {"date": "2024-01-15", "tasks": 5, "time": 8},
                {"date": "2024-01-14", "tasks": 3, "time": 6}
            ]
        }
        
        return area_insights
    except Exception as e:
        logger.error(f"Error getting area insights: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.get("/insights/projects/{project_id}")
async def get_project_insights(
    project_id: str,
    date_range: str = "all_time",
    current_user: User = Depends(get_current_active_user_hybrid)
):
    """Get insights for a specific project"""
    try:
        project_insights = {
            "project_id": project_id,
            "tasks_completed": 12,
            "tasks_remaining": 3,
            "completion_percentage": 80,
            "estimated_completion": "2024-01-20",
            "time_spent": 25, # hours
            "velocity": 2.4, # tasks per day
            "milestones": [
                {"name": "Phase 1", "completed": True, "date": "2024-01-10"},
                {"name": "Phase 2", "completed": False, "estimated": "2024-01-18"}
            ]
        }
        
        return project_insights
    except Exception as e:
        logger.error(f"Error getting project insights: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Include authentication routes under /api
api_router.include_router(auth_router, prefix="/auth")

# Include API router
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)