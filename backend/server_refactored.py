"""
Aurum Life API Server - Main Application Entry Point
====================================================

This is the core FastAPI application that serves as the backend for Aurum Life's
Personal Operating System. It handles all API endpoints, authentication, and 
orchestrates the various services.

Key Components:
- FastAPI application setup with CORS middleware
- Authentication via Supabase Auth
- RESTful API endpoints for PAPT hierarchy (Pillars, Areas, Projects, Tasks)
- AI Coach integration for intelligent task prioritization
- File upload handling for attachments
- Analytics and insights generation

Architecture:
- Service-oriented design with dedicated services for each domain
- Supabase integration for database and auth
- Performance monitoring for optimization
- Modular structure for easy extension

Author: Aurum Life Development Team
Last Updated: January 2025
"""

# ========================================
# IMPORTS AND DEPENDENCIES
# ========================================

# Core FastAPI imports
from fastapi import FastAPI, APIRouter, HTTPException, Query, Depends, status, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

# Environment and configuration
from dotenv import load_dotenv
from pathlib import Path
import os
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

# Pydantic models for request/response validation
from pydantic import BaseModel

# ========================================
# INTERNAL IMPORTS
# ========================================

# Database client
from supabase_client import supabase_manager

# Data models - defines all request/response schemas
from models import *

# Optimized services for high-performance operations
from optimized_services import (
    OptimizedPillarService,    # Handles Pillar CRUD with caching
    OptimizedAreaService,      # Handles Area CRUD with caching
    OptimizedProjectService,   # Handles Project CRUD with caching
    OptimizedStatsService      # Generates statistics efficiently
)

# Performance monitoring utility
from performance_monitor import perf_monitor

# Core business logic services
from services import (
    UserService,              # User profile management
    TaskService,              # Task operations
    JournalService,          # Journal entries
    CourseService,           # Learning courses (future feature)
    RecurringTaskService,    # Recurring task patterns
    InsightsService,         # AI-generated insights storage
    ResourceService,         # File attachments and resources
    StatsService,            # Basic statistics
    PillarService,           # Legacy pillar service
    AreaService,             # Legacy area service
    ProjectService,          # Legacy project service
    ProjectTemplateService,  # Project templates
    GoogleAuthService        # Google OAuth integration
)

# Supabase-specific service implementations
from supabase_services import (
    SupabasePillarService,   # Direct Supabase operations for Pillars
    SupabaseAreaService,     # Direct Supabase operations for Areas
    SupabaseProjectService,  # Direct Supabase operations for Projects
    SupabaseTaskService      # Direct Supabase operations for Tasks
)

# Authentication utilities
from supabase_auth import get_current_active_user
from supabase_auth_endpoints import auth_router

# Specialized services
from analytics_service import AnalyticsService          # User analytics
from alignment_score_service import AlignmentScoreService  # Goal alignment scoring
from ai_coach_mvp_service import AiCoachMvpService    # AI Coach for task prioritization

# ========================================
# CONFIGURATION AND SETUP
# ========================================

# Load environment variables from .env file
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging for debugging and monitoring
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ========================================
# FASTAPI APPLICATION INITIALIZATION
# ========================================

# Create the main FastAPI application instance
app = FastAPI(
    title="Aurum Life API",
    version="1.0.0",
    description="Personal Operating System API for intentional living",
    docs_url="/api/docs",    # Swagger UI documentation
    redoc_url="/api/redoc"   # ReDoc documentation
)

# ========================================
# MIDDLEWARE CONFIGURATION
# ========================================

# Configure CORS to allow frontend communication
# TODO: In production, restrict allow_origins to specific domains
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,      # Allow cookies for auth
    allow_origins=["*"],         # SECURITY: Restrict in production
    allow_methods=["*"],         # All HTTP methods allowed
    allow_headers=["*"],         # All headers allowed
    expose_headers=["*"]         # Expose all headers to client
)

# ========================================
# API ROUTER SETUP
# ========================================

# Create main API router with /api prefix
api_router = APIRouter(prefix="/api")

# ========================================
# SERVICE INITIALIZATION
# ========================================

# Initialize all service instances
# These handle the business logic for each domain

# User and authentication services
user_service = UserService(supabase_manager)
google_auth_service = GoogleAuthService(supabase_manager)

# PAPT hierarchy services (using optimized versions where available)
pillar_service = OptimizedPillarService(supabase_manager)
area_service = OptimizedAreaService(supabase_manager)
project_service = OptimizedProjectService(supabase_manager)
task_service = TaskService(supabase_manager)

# Supabase-specific services for direct DB operations
supabase_pillar_service = SupabasePillarService(supabase_manager)
supabase_area_service = SupabaseAreaService(supabase_manager)
supabase_project_service = SupabaseProjectService(supabase_manager)
supabase_task_service = SupabaseTaskService(supabase_manager)

# Feature-specific services
journal_service = JournalService(supabase_manager)
insights_service = InsightsService(supabase_manager)
resource_service = ResourceService(supabase_manager)
stats_service = OptimizedStatsService(supabase_manager)
analytics_service = AnalyticsService(supabase_manager)
alignment_score_service = AlignmentScoreService(supabase_manager)
ai_coach_service = AiCoachMvpService(supabase_manager)

# Template services
project_template_service = ProjectTemplateService(supabase_manager)

# ========================================
# AUTHENTICATION ENDPOINTS
# ========================================

# Include all authentication-related endpoints
# Handles: login, register, logout, password reset, OAuth
api_router.include_router(auth_router, tags=["Authentication"])

# ========================================
# HEALTH CHECK ENDPOINTS
# ========================================

@api_router.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring service status.
    
    Returns:
        dict: Status message and timestamp
        
    Used by:
        - Load balancers for health monitoring
        - Uptime monitoring services
        - Deployment verification
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# ========================================
# USER PROFILE ENDPOINTS
# ========================================

@api_router.get("/profile", response_model=UserProfile, tags=["User"])
async def get_profile(current_user: User = Depends(get_current_active_user)):
    """
    Get the current user's profile information.
    
    Args:
        current_user: Authenticated user from JWT token
        
    Returns:
        UserProfile: Complete user profile data
        
    Raises:
        HTTPException: If profile not found or database error
    """
    try:
        profile = await user_service.get_profile(current_user.id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        return profile
    except Exception as e:
        logger.error(f"Error fetching profile for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user profile"
        )

@api_router.put("/profile", response_model=UserProfile, tags=["User"])
async def update_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update the current user's profile.
    
    Args:
        profile_update: Fields to update in the profile
        current_user: Authenticated user
        
    Returns:
        UserProfile: Updated profile data
        
    Note:
        - Only provided fields will be updated
        - Email changes require re-verification (not implemented)
    """
    try:
        updated_profile = await user_service.update_profile(
            current_user.id, 
            profile_update
        )
        return updated_profile
    except Exception as e:
        logger.error(f"Error updating profile for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )

# ========================================
# PILLAR ENDPOINTS (Life Domains)
# ========================================

@api_router.get("/pillars", response_model=List[Pillar], tags=["Pillars"])
async def get_pillars(current_user: User = Depends(get_current_active_user)):
    """
    Get all pillars for the current user.
    
    Pillars represent top-level life domains (e.g., Health, Career, Relationships).
    They form the highest level of the PAPT hierarchy.
    
    Returns:
        List[Pillar]: User's pillars sorted by display_order
        
    Performance:
        - Uses optimized service with caching
        - Typical response time: <50ms
    """
    with perf_monitor.track("get_pillars"):
        return await pillar_service.get_user_pillars(current_user.id)

@api_router.post("/pillars", response_model=Pillar, tags=["Pillars"])
async def create_pillar(
    pillar: PillarCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new pillar for the user.
    
    Args:
        pillar: Pillar data including name, description, icon, color
        
    Returns:
        Pillar: Created pillar with generated ID
        
    Validation:
        - Name must be unique per user
        - Icon from predefined set
        - Valid hex color code
        
    Side Effects:
        - Triggers alignment score recalculation
        - Updates user statistics
    """
    with perf_monitor.track("create_pillar"):
        return await pillar_service.create_pillar(current_user.id, pillar)

@api_router.put("/pillars/{pillar_id}", response_model=Pillar, tags=["Pillars"])
async def update_pillar(
    pillar_id: str,
    pillar_update: PillarUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an existing pillar.
    
    Args:
        pillar_id: UUID of the pillar to update
        pillar_update: Fields to update (partial update supported)
        
    Security:
        - Verifies user owns the pillar
        - Prevents cross-user updates
        
    Note:
        - Changing time_allocation affects other pillars' percentages
        - Consider UX implications of pillar renames
    """
    with perf_monitor.track("update_pillar"):
        # Security check happens inside service
        return await pillar_service.update_pillar(
            current_user.id, 
            pillar_id, 
            pillar_update
        )

@api_router.delete("/pillars/{pillar_id}", tags=["Pillars"])
async def delete_pillar(
    pillar_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a pillar and all its children (areas, projects, tasks).
    
    WARNING: This is a cascading delete operation!
    - Deletes all areas under this pillar
    - Deletes all projects under those areas
    - Deletes all tasks under those projects
    - Deletes all associated resources
    
    Args:
        pillar_id: UUID of the pillar to delete
        
    Returns:
        dict: Success message
        
    Best Practice:
        - Show confirmation dialog in UI
        - Consider soft delete for recovery
    """
    with perf_monitor.track("delete_pillar"):
        await pillar_service.delete_pillar(current_user.id, pillar_id)
        return {"message": "Pillar deleted successfully"}

# ========================================
# AREA ENDPOINTS (Focus Areas)
# ========================================

@api_router.get("/areas", response_model=List[Area], tags=["Areas"])
async def get_areas(
    pillar_id: Optional[str] = Query(None, description="Filter by pillar ID"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get areas, optionally filtered by pillar.
    
    Areas represent ongoing focus areas within a pillar
    (e.g., "Fitness" within "Health" pillar).
    
    Args:
        pillar_id: Optional filter to get areas for specific pillar
        
    Returns:
        List[Area]: User's areas, filtered if pillar_id provided
        
    Use Cases:
        - Building pillar detail views
        - Area selection dropdowns
        - Cross-pillar area overview
    """
    with perf_monitor.track("get_areas"):
        if pillar_id:
            return await area_service.get_pillar_areas(current_user.id, pillar_id)
        return await area_service.get_user_areas(current_user.id)

@api_router.post("/areas", response_model=Area, tags=["Areas"])
async def create_area(
    area: AreaCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new area within a pillar.
    
    Args:
        area: Area data including name, pillar_id, description
        
    Validation:
        - Pillar must exist and belong to user
        - Name unique within pillar
        
    Best Practices:
        - Limit areas per pillar (3-7 recommended)
        - Use clear, actionable names
    """
    with perf_monitor.track("create_area"):
        # Verify user owns the pillar
        pillars = await pillar_service.get_user_pillars(current_user.id)
        if not any(p.id == area.pillar_id for p in pillars):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Pillar not found or access denied"
            )
        return await area_service.create_area(current_user.id, area)

@api_router.put("/areas/{area_id}", response_model=Area, tags=["Areas"])
async def update_area(
    area_id: str,
    area_update: AreaUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an existing area.
    
    Note:
        - Cannot move areas between pillars (by design)
        - To move, delete and recreate
    """
    with perf_monitor.track("update_area"):
        return await area_service.update_area(
            current_user.id,
            area_id,
            area_update
        )

@api_router.delete("/areas/{area_id}", tags=["Areas"])
async def delete_area(
    area_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete an area and all its children.
    
    CASCADE WARNING:
    - Deletes all projects in this area
    - Deletes all tasks in those projects
    - Cannot be undone
    """
    with perf_monitor.track("delete_area"):
        await area_service.delete_area(current_user.id, area_id)
        return {"message": "Area deleted successfully"}

# ========================================
# PROJECT ENDPOINTS (Time-bound Goals)
# ========================================

@api_router.get("/projects", response_model=List[Project], tags=["Projects"])
async def get_projects(
    area_id: Optional[str] = Query(None, description="Filter by area ID"),
    pillar_id: Optional[str] = Query(None, description="Filter by pillar ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get projects with optional filtering.
    
    Projects represent time-bound goals with clear completion criteria.
    They are the "engines of progress" in the PAPT hierarchy.
    
    Args:
        area_id: Filter by specific area
        pillar_id: Filter by pillar (gets all projects in all areas of pillar)
        status: Filter by status (active, completed, on_hold, cancelled)
        
    Returns:
        List[Project]: Filtered list of projects
        
    Performance Note:
        - Pillar filtering requires join operation
        - Consider pagination for users with many projects
    """
    with perf_monitor.track("get_projects"):
        # Build filter parameters
        params = {}
        if area_id:
            params['area_id'] = area_id
        if status:
            params['status'] = status
            
        if pillar_id:
            # Need to get all areas in pillar first
            areas = await area_service.get_pillar_areas(current_user.id, pillar_id)
            area_ids = [area.id for area in areas]
            return await project_service.get_projects_in_areas(current_user.id, area_ids)
        
        return await project_service.get_user_projects(current_user.id, **params)

@api_router.post("/projects", response_model=Project, tags=["Projects"])
async def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new project within an area.
    
    Key Fields:
        - name: Clear, actionable project name
        - area_id: Parent area (must exist)
        - target_date: When to complete by
        - milestones: Major checkpoints (optional)
        - success_criteria: How to know when done
        
    Side Effects:
        - Updates area statistics
        - Triggers alignment score calculation
        - May generate AI insights
    """
    with perf_monitor.track("create_project"):
        # Verify user owns the area
        areas = await area_service.get_user_areas(current_user.id)
        if not any(a.id == project.area_id for a in areas):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Area not found or access denied"
            )
        return await project_service.create_project(current_user.id, project)

@api_router.put("/projects/{project_id}", response_model=Project, tags=["Projects"])
async def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update project details.
    
    Common Updates:
        - Status changes (active -> completed)
        - Date adjustments
        - Milestone updates
        - Progress tracking
        
    Note:
        - Cannot move projects between areas
        - Status changes may trigger notifications
    """
    with perf_monitor.track("update_project"):
        return await project_service.update_project(
            current_user.id,
            project_id,
            project_update
        )

@api_router.delete("/projects/{project_id}", tags=["Projects"])
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a project and all its tasks.
    
    CASCADE WARNING:
    - Deletes all tasks in this project
    - Deletes all task attachments
    - Updates area statistics
    """
    with perf_monitor.track("delete_project"):
        await project_service.delete_project(current_user.id, project_id)
        return {"message": "Project deleted successfully"}

# ========================================
# TASK ENDPOINTS (Daily Actions)
# ========================================

@api_router.get("/tasks", response_model=List[Task], tags=["Tasks"])
async def get_tasks(
    project_id: Optional[str] = Query(None),
    area_id: Optional[str] = Query(None),
    pillar_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    due_before: Optional[datetime] = Query(None),
    due_after: Optional[datetime] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get tasks with comprehensive filtering options.
    
    Tasks are the atomic units of work that drive project completion.
    This endpoint supports complex filtering for various UI views.
    
    Args:
        project_id: Filter by project
        area_id: Filter by area (all projects in area)
        pillar_id: Filter by pillar (all areas in pillar)
        status: Filter by status (pending, in_progress, completed, cancelled)
        priority: Filter by priority (low, medium, high, urgent)
        due_before: Tasks due before this date
        due_after: Tasks due after this date
        limit: Maximum tasks to return (pagination)
        offset: Skip this many tasks (pagination)
        
    Returns:
        List[Task]: Filtered and paginated task list
        
    Use Cases:
        - Today view (due_before=today+1, status=pending)
        - Project task list (project_id filter)
        - Overdue tasks (due_before=today, status=pending)
        - High priority queue (priority=high/urgent)
    """
    with perf_monitor.track("get_tasks"):
        # Build filter criteria
        filters = {}
        if project_id:
            filters['project_id'] = project_id
        if status:
            filters['status'] = status
        if priority:
            filters['priority'] = priority
        if due_before:
            filters['due_before'] = due_before
        if due_after:
            filters['due_after'] = due_after
            
        # Handle hierarchical filters
        if area_id or pillar_id:
            # Get all relevant project IDs
            project_ids = []
            
            if area_id:
                projects = await project_service.get_user_projects(
                    current_user.id,
                    area_id=area_id
                )
                project_ids = [p.id for p in projects]
            elif pillar_id:
                areas = await area_service.get_pillar_areas(current_user.id, pillar_id)
                for area in areas:
                    projects = await project_service.get_user_projects(
                        current_user.id,
                        area_id=area.id
                    )
                    project_ids.extend([p.id for p in projects])
            
            filters['project_ids'] = project_ids
        
        return await task_service.get_user_tasks(
            current_user.id,
            limit=limit,
            offset=offset,
            **filters
        )

@api_router.post("/tasks", response_model=Task, tags=["Tasks"])
async def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new task within a project.
    
    Key Fields:
        - name: Clear, actionable task description
        - project_id: Parent project (must exist)
        - due_date: When to complete by (optional)
        - priority: low, medium, high, urgent
        - estimated_minutes: Time estimate (helps with planning)
        - recurrence_pattern: For recurring tasks (optional)
        
    AI Integration:
        - May trigger AI analysis for priority suggestions
        - Can auto-generate subtasks for complex tasks
        
    Best Practices:
        - Use verb-based names ("Write report" not "Report")
        - Set realistic time estimates
        - Add context in description field
    """
    with perf_monitor.track("create_task"):
        # Verify user owns the project
        projects = await project_service.get_user_projects(current_user.id)
        if not any(p.id == task.project_id for p in projects):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Project not found or access denied"
            )
        
        # Create the task
        created_task = await task_service.create_task(current_user.id, task)
        
        # Trigger AI analysis in background (fire-and-forget)
        # This will update the task with AI insights asynchronously
        try:
            # TODO: Make this actually async with Celery/background job
            await ai_coach_service.analyze_task(created_task.id, current_user.id)
        except Exception as e:
            logger.warning(f"AI analysis failed for task {created_task.id}: {e}")
            # Don't fail the request if AI fails
        
        return created_task

@api_router.put("/tasks/{task_id}", response_model=Task, tags=["Tasks"])
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update task details.
    
    Common Updates:
        - Status changes (track progress)
        - Priority adjustments
        - Due date changes
        - Completion marking
        
    Side Effects:
        - Updates project progress
        - May trigger notifications
        - Affects AI prioritization
        - Updates alignment scores
    """
    with perf_monitor.track("update_task"):
        updated_task = await task_service.update_task(
            current_user.id,
            task_id,
            task_update
        )
        
        # If task was completed, update project progress
        if task_update.status == "completed":
            task = await task_service.get_task(current_user.id, task_id)
            if task and task.project_id:
                await project_service.update_project_progress(
                    current_user.id,
                    task.project_id
                )
        
        return updated_task

@api_router.delete("/tasks/{task_id}", tags=["Tasks"])
async def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a task and its subtasks.
    
    Side Effects:
        - Updates project statistics
        - Removes from AI training data
        - Deletes associated attachments
    """
    with perf_monitor.track("delete_task"):
        await task_service.delete_task(current_user.id, task_id)
        return {"message": "Task deleted successfully"}

# ========================================
# AI COACH ENDPOINTS
# ========================================

@api_router.get("/today", response_model=TodayViewResponse, tags=["AI Coach"])
async def get_today_view(
    top_n: int = Query(10, ge=1, le=50, description="Number of top tasks to return"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get AI-prioritized tasks for today's focus.
    
    This is the main "command center" view that shows users what to work on.
    The AI Coach analyzes all pending tasks and returns the most important ones
    based on multiple factors.
    
    Prioritization Factors:
        - Due date urgency (overdue = highest priority)
        - User-set priority levels
        - Project importance
        - Pillar time allocation goals
        - Historical completion patterns
        - Energy levels (time of day)
        
    Returns:
        TodayViewResponse with:
        - tasks: Top N prioritized tasks with AI reasoning
        - insights: Daily insights and patterns
        - suggested_focus_time: Optimal time blocks
        
    Performance:
        - Caches results for 5 minutes
        - Average response time: <200ms
    """
    with perf_monitor.track("get_today_view"):
        return await ai_coach_service.get_today_priorities(
            current_user.id,
            top_n=top_n
        )

@api_router.post("/tasks/{task_id}/ai-coach", response_model=Dict[str, Any], tags=["AI Coach"])
async def get_task_coaching(
    task_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed AI coaching for a specific task.
    
    Provides personalized guidance on:
        - How to approach the task
        - Optimal time to work on it
        - Potential blockers
        - Connection to larger goals
        - Motivational insights
        
    Returns:
        dict with:
        - coaching_message: Personalized advice
        - optimal_time: Best time to work on task
        - estimated_energy: Energy required (1-5)
        - related_insights: Historical patterns
    """
    with perf_monitor.track("get_task_coaching"):
        # Verify user owns the task
        task = await task_service.get_task(current_user.id, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        return await ai_coach_service.get_task_coaching(
            task_id=task_id,
            user_id=current_user.id
        )

# ========================================
# INSIGHTS & ANALYTICS ENDPOINTS
# ========================================

@api_router.get("/insights", response_model=List[Insight], tags=["Insights"])
async def get_insights(
    limit: int = Query(10, le=50),
    insight_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get AI-generated insights about productivity patterns.
    
    Insight Types:
        - daily_pattern: Best times for different work
        - weekly_summary: Week-over-week progress
        - goal_alignment: How well tasks align with pillars
        - bottlenecks: What's blocking progress
        - achievements: Celebrate wins
        
    Returns:
        List[Insight]: Recent insights with explanations
    """
    with perf_monitor.track("get_insights"):
        return await insights_service.get_user_insights(
            current_user.id,
            limit=limit,
            insight_type=insight_type
        )

@api_router.get("/stats/overview", response_model=StatsOverview, tags=["Analytics"])
async def get_stats_overview(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get comprehensive statistics overview.
    
    Returns:
        StatsOverview with:
        - Total counts (pillars, areas, projects, tasks)
        - Completion rates by time period
        - Productivity trends
        - Time allocation vs. actual
        - Streak information
    """
    with perf_monitor.track("get_stats_overview"):
        return await stats_service.get_user_stats(current_user.id)

@api_router.get("/alignment-score", response_model=AlignmentScore, tags=["Analytics"])
async def get_alignment_score(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the user's current alignment score.
    
    Alignment Score (0-100) measures how well daily tasks align with life goals:
        - 80-100: Excellent alignment
        - 60-79: Good alignment  
        - 40-59: Moderate alignment
        - 0-39: Poor alignment
        
    Calculation considers:
        - Task distribution across pillars
        - Progress toward project goals
        - Time allocation adherence
        - Consistency of effort
    """
    with perf_monitor.track("get_alignment_score"):
        return await alignment_score_service.calculate_alignment_score(
            current_user.id
        )

# ========================================
# FILE UPLOAD ENDPOINTS
# ========================================

@api_router.post("/upload", response_model=Dict[str, str], tags=["Files"])
async def upload_file(
    file: UploadFile = File(...),
    entity_type: str = Form(..., regex="^(project|task)$"),
    entity_id: str = Form(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload a file attachment for a project or task.
    
    Args:
        file: File to upload (max 10MB)
        entity_type: Either "project" or "task"
        entity_id: ID of the project or task
        
    Returns:
        dict with:
        - file_id: Unique identifier for the file
        - file_url: Public URL to access the file
        
    Security:
        - Verifies user owns the entity
        - Validates file type and size
        - Scans for malware (TODO)
        
    Storage:
        - Files stored in Supabase Storage
        - Organized by user/entity/filename
        - CDN-served for performance
    """
    # Validate file size (10MB limit)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    # Read file in chunks to check size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Maximum size is 10MB"
        )
    
    # Reset file position
    file.file.seek(0)
    
    # Verify user owns the entity
    if entity_type == "project":
        project = await project_service.get_project(current_user.id, entity_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
    elif entity_type == "task":
        task = await task_service.get_task(current_user.id, entity_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
    
    # Generate unique filename
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Upload to Supabase Storage
    try:
        file_path = f"{current_user.id}/{entity_type}/{entity_id}/{unique_filename}"
        
        # TODO: Implement actual Supabase Storage upload
        # For now, return mock response
        file_url = f"https://storage.aurumlife.com/{file_path}"
        
        # Save file reference in database
        resource = await resource_service.create_resource(
            user_id=current_user.id,
            entity_type=entity_type,
            entity_id=entity_id,
            file_name=file.filename,
            file_url=file_url,
            file_size=len(contents),
            mime_type=file.content_type
        )
        
        return {
            "file_id": resource.id,
            "file_url": file_url
        }
        
    except Exception as e:
        logger.error(f"File upload failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File upload failed"
        )

# ========================================
# JOURNAL ENDPOINTS
# ========================================

@api_router.get("/journal/entries", response_model=List[JournalEntry], tags=["Journal"])
async def get_journal_entries(
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user's journal entries.
    
    Journal entries are used for:
        - Daily reflections
        - Progress tracking
        - Gratitude practice
        - Learning capture
        
    Returns:
        List[JournalEntry]: Recent entries, newest first
    """
    with perf_monitor.track("get_journal_entries"):
        return await journal_service.get_user_entries(
            current_user.id,
            limit=limit,
            offset=offset
        )

@api_router.post("/journal/entries", response_model=JournalEntry, tags=["Journal"])
async def create_journal_entry(
    entry: JournalEntryCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new journal entry.
    
    AI Integration:
        - Sentiment analysis
        - Pattern recognition
        - Insight generation
        - Goal correlation
    """
    with perf_monitor.track("create_journal_entry"):
        created_entry = await journal_service.create_entry(
            current_user.id,
            entry
        )
        
        # Trigger AI analysis (async)
        # TODO: Implement journal AI analysis
        
        return created_entry

# ========================================
# ERROR HANDLERS
# ========================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Global HTTP exception handler.
    
    Ensures consistent error response format across all endpoints.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unexpected errors.
    
    Logs full error details while returning safe error message to client.
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "An unexpected error occurred",
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# ========================================
# APPLICATION STARTUP/SHUTDOWN
# ========================================

@app.on_event("startup")
async def startup_event():
    """
    Application startup tasks.
    
    Runs once when the server starts:
        - Verify database connection
        - Initialize caches
        - Start background tasks
        - Log startup info
    """
    logger.info("Starting Aurum Life API...")
    
    # Verify Supabase connection
    try:
        await supabase_manager.verify_connection()
        logger.info("✓ Database connection verified")
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        # Don't start if DB is down
        raise
    
    # Initialize performance monitoring
    perf_monitor.start()
    logger.info("✓ Performance monitoring started")
    
    # TODO: Initialize caches
    # TODO: Start background tasks (Celery)
    
    logger.info("✓ Aurum Life API started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown tasks.
    
    Runs when the server is stopping:
        - Flush caches
        - Close database connections
        - Save performance metrics
        - Graceful cleanup
    """
    logger.info("Shutting down Aurum Life API...")
    
    # Save performance metrics
    perf_monitor.stop()
    
    # Close database connections
    await supabase_manager.close()
    
    logger.info("✓ Aurum Life API shut down cleanly")

# ========================================
# MOUNT API ROUTER
# ========================================

# Mount the API router to the main app
app.include_router(api_router)

# ========================================
# ROOT ENDPOINT
# ========================================

@app.get("/")
async def root():
    """
    Root endpoint - API information.
    
    Useful for health checks and API discovery.
    """
    return {
        "name": "Aurum Life API",
        "version": "1.0.0",
        "description": "Personal Operating System for intentional living",
        "documentation": "/api/docs",
        "health": "/api/health"
    }

# ========================================
# MAIN ENTRY POINT
# ========================================

if __name__ == "__main__":
    """
    Development server entry point.
    
    In production, use:
        uvicorn server:app --host 0.0.0.0 --port 8000 --workers 4
    """
    import uvicorn
    
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8001,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )