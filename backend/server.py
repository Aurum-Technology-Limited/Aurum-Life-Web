from fastapi import FastAPI, APIRouter, HTTPException, Query, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from dotenv import load_dotenv
from pathlib import Path
import os
import logging
from typing import List, Optional
from datetime import timedelta

# Import our models and services
from supabase_client import supabase_manager
from models import *
from services import *
from notification_service import notification_service
from auth import get_current_active_user as old_get_current_active_user, verify_token as old_verify_token, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, verify_password

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create the main app
app = FastAPI(title="Aurum Life API", version="1.0.0")

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

def get_current_active_user(*args, **kwargs):
    """Use the old auth system for compatibility"""
    return old_get_current_active_user(*args, **kwargs)

# Health check endpoints
@api_router.get("/")
async def root():
    return {"message": "Aurum Life API is running", "version": "1.0.0"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "aurum-life-api"}

# Authentication endpoints
@api_router.post("/auth/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    """Register a new user"""
    try:
        user = await UserService.create_user(user_data)
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            level=user.level,
            total_points=user.total_points,
            current_streak=user.current_streak,
            created_at=user.created_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.post("/auth/login", response_model=Token)
async def login_user(user_credentials: UserLogin):
    """Login user and return access token"""
    try:
        user = await UserService.authenticate_user(user_credentials.email, user_credentials.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.post("/auth/google", response_model=GoogleAuthResponse)
async def google_auth(auth_request: GoogleAuthRequest):
    """Authenticate user with Google OAuth"""
    try:
        # Verify the Google token
        google_user_info = await GoogleAuthService.verify_google_token(auth_request.token)
        if not google_user_info:
            raise HTTPException(status_code=401, detail="Invalid Google token")
        
        # Find or create user
        user = await GoogleAuthService.authenticate_or_create_user(google_user_info)
        if not user:
            raise HTTPException(status_code=500, detail="Failed to authenticate user")
        
        # Create JWT token
        token_data = {"sub": user.email}
        access_token = create_access_token(token_data, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        
        return GoogleAuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=user
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google auth error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        is_active=current_user.is_active,
        level=current_user.level,
        total_points=current_user.total_points,
        current_streak=current_user.current_streak,
        created_at=current_user.created_at
    )

@api_router.post("/auth/forgot-password", response_model=PasswordResetResponse)
async def request_password_reset(reset_request: PasswordResetRequest):
    """Request password reset email"""
    try:
        from email_service import email_service
        
        # Generate reset token
        reset_token = await UserService.create_password_reset_token(reset_request.email)
        
        if not reset_token:
            # For security, don't reveal whether email exists or not
            return PasswordResetResponse(
                message="If an account with that email exists, a password reset link has been sent.",
                success=True
            )
        
        # Get user information for personalized email
        user = await UserService.get_user_by_email(reset_request.email)
        user_name = user.first_name if user and user.first_name else "User"
        
        # Send password reset email
        try:
            await email_service.send_password_reset_email(
                email=reset_request.email,
                reset_token=reset_token,
                user_name=user_name
            )
            logger.info(f"Password reset email sent to {reset_request.email}")
        except Exception as e:
            logger.error(f"Failed to send password reset email to {reset_request.email}: {str(e)}")
            # Don't expose email sending errors to user
            pass
        
        return PasswordResetResponse(
            message="If an account with that email exists, a password reset link has been sent.",
            success=True
        )
        
    except Exception as e:
        logger.error(f"Password reset request failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process password reset request"
        )

@api_router.post("/auth/reset-password", response_model=PasswordResetResponse)
async def confirm_password_reset(reset_confirm: PasswordResetConfirm):
    """Confirm password reset with token and new password"""
    try:
        # Validate password length
        if len(reset_confirm.new_password) < 6:
            return PasswordResetResponse(
                message="Password must be at least 6 characters long.",
                success=False
            )
        
        # Reset password
        success = await UserService.reset_password(
            token=reset_confirm.token,
            new_password=reset_confirm.new_password
        )
        
        if success:
            return PasswordResetResponse(
                message="Password has been reset successfully. You can now login with your new password.",
                success=True
            )
        else:
            return PasswordResetResponse(
                message="Invalid or expired reset token. Please request a new password reset.",
                success=False
            )
            
    except Exception as e:
        logger.error(f"Password reset confirmation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password"
        )

class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None

@api_router.put("/users/me", response_model=dict)
async def update_current_user_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update current user's profile information"""
    try:
        success = await UserService.update_user_profile(
            current_user.id, 
            profile_data.first_name, 
            profile_data.last_name
        )
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update profile")
        return {"success": True, "message": "Profile updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# User endpoints (keeping existing functionality for demo purposes)
@api_router.post("/users", response_model=User)
async def create_user(user_data: UserCreate):
    """Create a new user (legacy endpoint)"""
    try:
        return await UserService.create_user(user_data)
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/users/{user_id}", response_model=User)
async def get_user(current_user: User = Depends(get_current_active_user)):
    """Get current user"""
    return current_user

@api_router.put("/users/{user_id}", response_model=dict)
async def update_user(user_data: UserUpdate, current_user: User = Depends(get_current_active_user)):
    """Update user"""
    success = await UserService.update_user(current_user.id, user_data)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"success": True, "message": "User updated successfully"}

# Dashboard endpoint
@api_router.get("/dashboard", response_model=UserDashboard)
async def get_dashboard(current_user: User = Depends(get_current_active_user)):
    """Get dashboard data for user"""
    try:
        return await StatsService.get_dashboard_data(current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced Journal endpoints
@api_router.post("/journal", response_model=JournalEntry)
async def create_journal_entry(entry_data: JournalEntryCreate, current_user: User = Depends(get_current_active_user)):
    """Create a new journal entry"""
    try:
        return await JournalService.create_entry(current_user.id, entry_data)
    except Exception as e:
        logger.error(f"Error creating journal entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/journal", response_model=List[JournalEntryResponse])
async def get_journal_entries(
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    mood_filter: Optional[str] = Query(None, description="Filter by mood"),
    tag_filter: Optional[str] = Query(None, description="Filter by tag"),
    date_from: Optional[datetime] = Query(None, description="Filter from date"),
    date_to: Optional[datetime] = Query(None, description="Filter to date")
):
    """Get journal entries for user with advanced filtering"""
    try:
        return await JournalService.get_user_entries(
            current_user.id, skip, limit, mood_filter, tag_filter, date_from, date_to
        )
    except Exception as e:
        logger.error(f"Error getting journal entries: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/journal/search", response_model=List[JournalEntryResponse])
async def search_journal_entries(
    q: str = Query(..., description="Search term"),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user)
):
    """Search journal entries by content"""
    try:
        return await JournalService.search_entries(current_user.id, q, limit)
    except Exception as e:
        logger.error(f"Error searching journal entries: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/journal/on-this-day", response_model=List[OnThisDayEntry])
async def get_on_this_day_entries(
    date: Optional[datetime] = Query(None, description="Target date (default: today)"),
    current_user: User = Depends(get_current_active_user)
):
    """Get journal entries from the same date in previous years"""
    try:
        return await JournalService.get_on_this_day(current_user.id, date)
    except Exception as e:
        logger.error(f"Error getting on this day entries: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/journal/insights", response_model=JournalInsights)
async def get_journal_insights(current_user: User = Depends(get_current_active_user)):
    """Get comprehensive journal analytics and insights"""
    try:
        return await JournalService.get_journal_insights(current_user.id)
    except Exception as e:
        logger.error(f"Error getting journal insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/journal/{entry_id}", response_model=dict)
async def update_journal_entry(entry_id: str, entry_data: JournalEntryUpdate, current_user: User = Depends(get_current_active_user)):
    """Update a journal entry"""
    success = await JournalService.update_entry(current_user.id, entry_id, entry_data)
    if not success:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return {"success": True, "message": "Journal entry updated successfully"}

@api_router.delete("/journal/{entry_id}", response_model=dict)
async def delete_journal_entry(entry_id: str, current_user: User = Depends(get_current_active_user)):
    """Delete a journal entry"""
    success = await JournalService.delete_entry(current_user.id, entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return {"success": True, "message": "Journal entry deleted successfully"}

# Journal Templates endpoints
@api_router.get("/journal/templates", response_model=List[JournalTemplate])
async def get_journal_templates(current_user: User = Depends(get_current_active_user)):
    """Get all journal templates for the user (including default templates)"""
    try:
        return await JournalService.get_user_templates(current_user.id)
    except Exception as e:
        logger.error(f"Error getting journal templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/journal/templates/{template_id}", response_model=JournalTemplate)
async def get_journal_template(template_id: str, current_user: User = Depends(get_current_active_user)):
    """Get a specific journal template"""
    try:
        template = await JournalService.get_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return template
    except Exception as e:
        logger.error(f"Error getting journal template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/journal/templates", response_model=JournalTemplate)
async def create_journal_template(template_data: JournalTemplateCreate, current_user: User = Depends(get_current_active_user)):
    """Create a new custom journal template"""
    try:
        return await JournalService.create_template(current_user.id, template_data)
    except Exception as e:
        logger.error(f"Error creating journal template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/journal/templates/{template_id}", response_model=dict)
async def update_journal_template(template_id: str, template_data: JournalTemplateUpdate, current_user: User = Depends(get_current_active_user)):
    """Update a custom journal template"""
    try:
        success = await JournalService.update_template(current_user.id, template_id, template_data)
        if not success:
            raise HTTPException(status_code=404, detail="Template not found or not owned by user")
        return {"success": True, "message": "Template updated successfully"}
    except Exception as e:
        logger.error(f"Error updating journal template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/journal/templates/{template_id}", response_model=dict)
async def delete_journal_template(template_id: str, current_user: User = Depends(get_current_active_user)):
    """Delete a custom journal template"""
    try:
        success = await JournalService.delete_template(current_user.id, template_id)
        if not success:
            raise HTTPException(status_code=404, detail="Template not found or not owned by user")
        return {"success": True, "message": "Template deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting journal template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Project Templates endpoints
@api_router.get("/project-templates", response_model=List[ProjectTemplateResponse])
async def get_project_templates(current_user: User = Depends(get_current_active_user)):
    """Get all project templates for the current user"""
    return await ProjectTemplateService.get_user_templates(current_user.id)

@api_router.post("/project-templates", response_model=ProjectTemplateResponse)
async def create_project_template(template_data: ProjectTemplateCreate, current_user: User = Depends(get_current_active_user)):
    """Create a new project template"""
    template = await ProjectTemplateService.create_template(current_user.id, template_data)
    return await ProjectTemplateService.get_template(current_user.id, template.id)

@api_router.get("/project-templates/{template_id}", response_model=ProjectTemplateResponse)
async def get_project_template(template_id: str, current_user: User = Depends(get_current_active_user)):
    """Get a specific project template"""
    template = await ProjectTemplateService.get_template(current_user.id, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@api_router.put("/project-templates/{template_id}", response_model=ProjectTemplateResponse)
async def update_project_template(template_id: str, template_data: ProjectTemplateUpdate, current_user: User = Depends(get_current_active_user)):
    """Update a project template"""
    success = await ProjectTemplateService.update_template(current_user.id, template_id, template_data)
    if not success:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return await ProjectTemplateService.get_template(current_user.id, template_id)

@api_router.delete("/project-templates/{template_id}")
async def delete_project_template(template_id: str, current_user: User = Depends(get_current_active_user)):
    """Delete a project template"""
    success = await ProjectTemplateService.delete_template(current_user.id, template_id)
    if not success:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return {"message": "Template deleted successfully"}

@api_router.post("/project-templates/{template_id}/use", response_model=ProjectResponse)
async def use_project_template(template_id: str, project_data: ProjectCreate, current_user: User = Depends(get_current_active_user)):
    """Create a new project from a template"""
    try:
        project = await ProjectTemplateService.use_template(current_user.id, template_id, project_data)
        return await ProjectService.get_project(current_user.id, project.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Pillar endpoints
@api_router.post("/pillars", response_model=Pillar)
async def create_pillar(pillar_data: PillarCreate, current_user: User = Depends(get_current_active_user)):
    """Create a new pillar"""
    try:
        return await PillarService.create_pillar(current_user.id, pillar_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating pillar: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/pillars", response_model=List[PillarResponse])
async def get_pillars(
    include_areas: bool = Query(False, description="Include linked areas"),
    include_archived: bool = Query(False, description="Include archived pillars"),
    current_user: User = Depends(get_current_active_user)
):
    """Get all pillars for user"""
    try:
        return await PillarService.get_user_pillars(current_user.id, include_areas, include_archived)
    except Exception as e:
        logger.error(f"Error getting pillars: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/pillars/{pillar_id}", response_model=PillarResponse)
async def get_pillar(
    pillar_id: str, 
    include_areas: bool = Query(False, description="Include linked areas"),
    current_user: User = Depends(get_current_active_user)
):
    """Get pillar by ID"""
    pillar = await PillarService.get_pillar(current_user.id, pillar_id, include_areas)
    if not pillar:
        raise HTTPException(status_code=404, detail="Pillar not found")
    return pillar

@api_router.put("/pillars/{pillar_id}", response_model=dict)
async def update_pillar(pillar_id: str, pillar_data: PillarUpdate, current_user: User = Depends(get_current_active_user)):
    """Update a pillar"""
    try:
        success = await PillarService.update_pillar(current_user.id, pillar_id, pillar_data)
        if not success:
            raise HTTPException(status_code=404, detail="Pillar not found")
        return {"success": True, "message": "Pillar updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating pillar: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/pillars/{pillar_id}/archive")
async def archive_pillar(pillar_id: str, current_user: User = Depends(get_current_active_user)):
    """Archive a pillar"""
    success = await PillarService.archive_pillar(current_user.id, pillar_id)
    if not success:
        raise HTTPException(status_code=404, detail="Pillar not found")
    return {"message": "Pillar archived successfully"}

@api_router.put("/pillars/{pillar_id}/unarchive")
async def unarchive_pillar(pillar_id: str, current_user: User = Depends(get_current_active_user)):
    """Unarchive a pillar"""
    success = await PillarService.unarchive_pillar(current_user.id, pillar_id)
    if not success:
        raise HTTPException(status_code=404, detail="Pillar not found")
    return {"message": "Pillar unarchived successfully"}

@api_router.delete("/pillars/{pillar_id}", response_model=dict)
async def delete_pillar(pillar_id: str, current_user: User = Depends(get_current_active_user)):
    """Delete a pillar and unlink associated areas"""
    success = await PillarService.delete_pillar(current_user.id, pillar_id)
    if not success:
        raise HTTPException(status_code=404, detail="Pillar not found")
    return {"success": True, "message": "Pillar deleted successfully"}

# Area endpoints
@api_router.post("/areas", response_model=Area)
async def create_area(area_data: AreaCreate, current_user: User = Depends(get_current_active_user)):
    """Create a new area"""
    try:
        return await AreaService.create_area(current_user.id, area_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating area: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/areas", response_model=List[AreaResponse])
async def get_areas(
    include_projects: bool = Query(False),
    include_archived: bool = Query(False, description="Include archived areas"),
    current_user: User = Depends(get_current_active_user)
):
    """Get all areas for user"""
    try:
        return await AreaService.get_user_areas(current_user.id, include_projects, include_archived)
    except Exception as e:
        logger.error(f"Error getting areas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/areas/{area_id}", response_model=AreaResponse)
async def get_area(area_id: str, current_user: User = Depends(get_current_active_user)):
    """Get area by ID with projects"""
    area = await AreaService.get_area(current_user.id, area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    return area

@api_router.put("/areas/{area_id}", response_model=dict)
async def update_area(area_id: str, area_data: AreaUpdate, current_user: User = Depends(get_current_active_user)):
    """Update an area"""
    success = await AreaService.update_area(current_user.id, area_id, area_data)
    if not success:
        raise HTTPException(status_code=404, detail="Area not found")
    return {"success": True, "message": "Area updated successfully"}

@api_router.put("/areas/{area_id}/archive")
async def archive_area(area_id: str, current_user: User = Depends(get_current_active_user)):
    """Archive an area"""
    success = await AreaService.archive_area(current_user.id, area_id)
    if not success:
        raise HTTPException(status_code=404, detail="Area not found")
    return {"message": "Area archived successfully"}

@api_router.put("/areas/{area_id}/unarchive")
async def unarchive_area(area_id: str, current_user: User = Depends(get_current_active_user)):
    """Unarchive an area"""
    success = await AreaService.unarchive_area(current_user.id, area_id)
    if not success:
        raise HTTPException(status_code=404, detail="Area not found")
    return {"message": "Area unarchived successfully"}

@api_router.delete("/areas/{area_id}", response_model=dict)
async def delete_area(area_id: str, current_user: User = Depends(get_current_active_user)):
    """Delete an area and all its projects/tasks"""
    success = await AreaService.delete_area(current_user.id, area_id)
    if not success:
        raise HTTPException(status_code=404, detail="Area not found")
    return {"success": True, "message": "Area deleted successfully"}

# Project endpoints
@api_router.post("/projects", response_model=Project)
async def create_project(project_data: ProjectCreate, current_user: User = Depends(get_current_active_user)):
    """Create a new project"""
    try:
        return await ProjectService.create_project(current_user.id, project_data)
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/projects", response_model=List[ProjectResponse])
async def get_projects(
    area_id: Optional[str] = Query(None, description="Filter by area ID"),
    include_archived: bool = Query(False, description="Include archived projects"),
    current_user: User = Depends(get_current_active_user)
):
    """Get all projects for user, optionally filtered by area"""
    try:
        return await ProjectService.get_user_projects(current_user.id, area_id, include_archived)
    except Exception as e:
        logger.error(f"Error getting projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str, 
    include_tasks: bool = Query(False),
    current_user: User = Depends(get_current_active_user)
):
    """Get project by ID"""
    project = await ProjectService.get_project(current_user.id, project_id, include_tasks)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@api_router.put("/projects/{project_id}", response_model=dict)
async def update_project(project_id: str, project_data: ProjectUpdate, current_user: User = Depends(get_current_active_user)):
    """Update a project"""
    success = await ProjectService.update_project(current_user.id, project_id, project_data)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"success": True, "message": "Project updated successfully"}

@api_router.put("/projects/{project_id}/archive")
async def archive_project(project_id: str, current_user: User = Depends(get_current_active_user)):
    """Archive a project"""
    success = await ProjectService.archive_project(current_user.id, project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project archived successfully"}

@api_router.put("/projects/{project_id}/unarchive")
async def unarchive_project(project_id: str, current_user: User = Depends(get_current_active_user)):
    """Unarchive a project"""
    success = await ProjectService.unarchive_project(current_user.id, project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project unarchived successfully"}

@api_router.delete("/projects/{project_id}", response_model=dict)
async def delete_project(project_id: str, current_user: User = Depends(get_current_active_user)):
    """Delete a project and all its tasks"""
    success = await ProjectService.delete_project(current_user.id, project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"success": True, "message": "Project deleted successfully"}

# Enhanced Task endpoints
@api_router.get("/projects/{project_id}/tasks", response_model=List[TaskResponse])
async def get_project_tasks(project_id: str, current_user: User = Depends(get_current_active_user)):
    """Get all tasks for a specific project"""
    try:
        return await TaskService.get_project_tasks(project_id)
    except Exception as e:
        logger.error(f"Error getting project tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/projects/{project_id}/kanban", response_model=KanbanBoard)
async def get_kanban_board(project_id: str, current_user: User = Depends(get_current_active_user)):
    """Get kanban board for a project"""
    try:
        return await TaskService.get_kanban_board(current_user.id, project_id)
    except Exception as e:
        logger.error(f"Error getting kanban board: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/tasks/{task_id}/column", response_model=dict)
async def move_task_column(task_id: str, new_column: str, current_user: User = Depends(get_current_active_user)):
    """Move task to different kanban column"""
    success = await TaskService.move_task_column(current_user.id, task_id, new_column)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid column or task not found")
    return {"success": True, "message": "Task moved successfully"}

@api_router.get("/today", response_model=TodayView)
async def get_today_view(current_user: User = Depends(get_current_active_user)):
    """Get today's focused view"""
    try:
        return await StatsService.get_today_view(current_user.id)
    except Exception as e:
        logger.error(f"Error getting today view: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Update existing task endpoints to work with new structure
# Task endpoints (updated for project integration)
@api_router.post("/tasks", response_model=Task)
async def create_task(task_data: TaskCreate, current_user: User = Depends(get_current_active_user)):
    """Create a new task"""
    try:
        return await TaskService.create_task(current_user.id, task_data)
    except ValueError as e:
        logger.error(f"Validation error creating task: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(
    project_id: str = Query(None),
    current_user: User = Depends(get_current_active_user)
):
    """Get all tasks for user, optionally filtered by project"""
    try:
        return await TaskService.get_user_tasks(current_user.id, project_id)
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/tasks/{task_id}", response_model=dict)
async def update_task(task_id: str, task_data: TaskUpdate, current_user: User = Depends(get_current_active_user)):
    """Update a task"""
    try:
        success = await TaskService.update_task(current_user.id, task_id, task_data)
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"success": True, "message": "Task updated successfully"}
    except ValueError as e:
        # Handle dependency validation errors (FR-1.1.3)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.delete("/tasks/{task_id}", response_model=dict)
async def delete_task(task_id: str, current_user: User = Depends(get_current_active_user)):
    """Delete a task"""
    success = await TaskService.delete_task(current_user.id, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"success": True, "message": "Task deleted successfully"}

# Task Dependencies Endpoints (SR-1.1)
@api_router.get("/tasks/{task_id}/dependencies", response_model=dict)
async def get_task_dependencies(task_id: str, current_user: User = Depends(get_current_active_user)):
    """Get task dependencies and their completion status"""
    try:
        task_with_deps = await TaskService.get_task_with_dependencies(current_user.id, task_id)
        if not task_with_deps:
            raise HTTPException(status_code=404, detail="Task not found")
        return {
            "task_id": task_id,
            "dependency_task_ids": task_with_deps.dependency_task_ids,
            "dependency_tasks": task_with_deps.dependency_tasks,
            "can_start": task_with_deps.can_start
        }
    except Exception as e:
        logger.error(f"Error getting task dependencies for {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.put("/tasks/{task_id}/dependencies", response_model=dict)
async def update_task_dependencies(task_id: str, dependency_ids: List[str], current_user: User = Depends(get_current_active_user)):
    """Update task dependencies"""
    try:
        success = await TaskService.update_task_dependencies(current_user.id, task_id, dependency_ids)
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"success": True, "message": "Task dependencies updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating task dependencies for {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.get("/projects/{project_id}/tasks/available-dependencies", response_model=List[dict])
async def get_available_dependency_tasks(project_id: str, task_id: Optional[str] = None, current_user: User = Depends(get_current_active_user)):
    """Get tasks that can be used as dependencies for a specific task"""
    try:
        available_tasks = await TaskService.get_available_dependency_tasks(current_user.id, project_id, task_id)
        return available_tasks
    except Exception as e:
        logger.error(f"Error getting available dependency tasks for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Sub-task endpoints
@api_router.post("/tasks/{parent_task_id}/subtasks", response_model=Task)
async def create_subtask(parent_task_id: str, subtask_data: TaskCreate, current_user: User = Depends(get_current_active_user)):
    """Create a sub-task under a parent task"""
    try:
        return await TaskService.create_subtask(current_user.id, parent_task_id, subtask_data)
    except ValueError as e:
        logger.error(f"Validation error creating subtask: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating subtask: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/tasks/{task_id}/with-subtasks", response_model=TaskResponse)
async def get_task_with_subtasks(task_id: str, current_user: User = Depends(get_current_active_user)):
    """Get a task with all its sub-tasks"""
    task = await TaskService.get_task_with_subtasks(current_user.id, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@api_router.get("/tasks/{task_id}/subtasks", response_model=List[TaskResponse])
async def get_subtasks(task_id: str, current_user: User = Depends(get_current_active_user)):
    """Get all sub-tasks of a parent task"""
    try:
        subtasks_docs = await find_documents("tasks", {"parent_task_id": task_id, "user_id": current_user.id})
        subtasks_docs.sort(key=lambda x: x.get("sort_order", 0))
        
        subtasks = []
        for doc in subtasks_docs:
            subtask = await TaskService._build_task_response(doc, include_subtasks=False)
            subtasks.append(subtask)
        
        return subtasks
    except Exception as e:
        logger.error(f"Error getting subtasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Daily Task Curation endpoints
@api_router.get("/today/available-tasks", response_model=List[TaskResponse])
async def get_available_tasks_for_today(current_user: User = Depends(get_current_active_user)):
    """Get tasks available to add to today's curated view"""
    try:
        return await TaskService.get_available_tasks_for_today(current_user.id)
    except Exception as e:
        logger.error(f"Error getting available tasks for today: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/today/tasks/{task_id}")
async def add_task_to_today(task_id: str, current_user: User = Depends(get_current_active_user)):
    """Add a task to today's curated list"""
    try:
        success = await TaskService.add_task_to_today(current_user.id, task_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to add task to today")
        return {"message": "Task added to today successfully"}
    except ValueError as e:
        logger.error(f"Validation error adding task to today: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding task to today: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/today/tasks/{task_id}")
async def remove_task_from_today(task_id: str, current_user: User = Depends(get_current_active_user)):
    """Remove a task from today's curated list"""
    try:
        success = await TaskService.remove_task_from_today(current_user.id, task_id)
        if not success:
            raise HTTPException(status_code=404, detail="Task not found in today's list")
        return {"message": "Task removed from today successfully"}
    except Exception as e:
        logger.error(f"Error removing task from today: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/today/reorder")
async def reorder_daily_tasks(task_data: DailyTasksUpdate, current_user: User = Depends(get_current_active_user)):
    """Reorder tasks in today's view"""
    try:
        success = await TaskService.reorder_daily_tasks(current_user.id, task_data.task_ids)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to reorder daily tasks")
        return {"message": "Daily tasks reordered successfully"}
    except Exception as e:
        logger.error(f"Error reordering daily tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/projects/{project_id}/tasks/reorder")
async def reorder_project_tasks(project_id: str, task_data: DailyTasksUpdate, current_user: User = Depends(get_current_active_user)):
    """Reorder tasks within a project"""
    try:
        success = await TaskService.reorder_project_tasks(current_user.id, project_id, task_data.task_ids)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to reorder project tasks")
        return {"message": "Project tasks reordered successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error reordering project tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Recurring Tasks endpoints
@api_router.get("/recurring-tasks", response_model=List[RecurringTaskResponse])
async def get_recurring_tasks(current_user: User = Depends(get_current_active_user)):
    """Get all recurring task templates for the user"""
    try:
        return await RecurringTaskService.get_user_recurring_tasks(current_user.id)
    except Exception as e:
        logger.error(f"Error getting recurring tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/recurring-tasks", response_model=RecurringTaskTemplate)
async def create_recurring_task(task_data: RecurringTaskCreate, current_user: User = Depends(get_current_active_user)):
    """Create a new recurring task template"""
    try:
        return await RecurringTaskService.create_recurring_task(current_user.id, task_data)
    except ValueError as e:
        logger.error(f"Validation error creating recurring task: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating recurring task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/recurring-tasks/{template_id}")
async def update_recurring_task(template_id: str, task_data: RecurringTaskUpdate, current_user: User = Depends(get_current_active_user)):
    """Update a recurring task template"""
    try:
        success = await RecurringTaskService.update_recurring_task(current_user.id, template_id, task_data)
        if not success:
            raise HTTPException(status_code=404, detail="Recurring task template not found")
        return {"message": "Recurring task updated successfully"}
    except Exception as e:
        logger.error(f"Error updating recurring task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/recurring-tasks/{template_id}")
async def delete_recurring_task(template_id: str, current_user: User = Depends(get_current_active_user)):
    """Delete a recurring task template and all its instances"""
    try:
        success = await RecurringTaskService.delete_recurring_task(current_user.id, template_id)
        if not success:
            raise HTTPException(status_code=404, detail="Recurring task template not found")
        return {"message": "Recurring task deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting recurring task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/recurring-tasks/{template_id}/instances", response_model=List[RecurringTaskInstance])
async def get_recurring_task_instances(
    template_id: str,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user)
):
    """Get instances of a recurring task template"""
    try:
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        return await RecurringTaskService.get_recurring_task_instances(
            current_user.id, template_id, start_dt, end_dt
        )
    except Exception as e:
        logger.error(f"Error getting recurring task instances: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/recurring-task-instances/{instance_id}/complete")
async def complete_recurring_task_instance(instance_id: str, current_user: User = Depends(get_current_active_user)):
    """Complete a recurring task instance"""
    try:
        success = await RecurringTaskService.complete_recurring_task_instance(current_user.id, instance_id)
        if not success:
            raise HTTPException(status_code=404, detail="Recurring task instance not found")
        return {"message": "Recurring task instance completed"}
    except Exception as e:
        logger.error(f"Error completing recurring task instance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/recurring-task-instances/{instance_id}/skip")
async def skip_recurring_task_instance(instance_id: str, current_user: User = Depends(get_current_active_user)):
    """Skip a recurring task instance"""
    try:
        success = await RecurringTaskService.skip_recurring_task_instance(current_user.id, instance_id)
        if not success:
            raise HTTPException(status_code=404, detail="Recurring task instance not found")
        return {"message": "Recurring task instance skipped"}
    except Exception as e:
        logger.error(f"Error skipping recurring task instance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/recurring-tasks/generate-instances")
async def trigger_recurring_task_generation(current_user: User = Depends(get_current_active_user)):
    """Manually trigger recurring task instance generation (admin/testing)"""
    try:
        await RecurringTaskService.generate_recurring_task_instances()
        return {"message": "Recurring task instances generated successfully"}
    except Exception as e:
        logger.error(f"Error generating recurring task instances: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Chat endpoints
@api_router.post("/chat", response_model=ChatMessage)
async def send_chat_message(message_data: ChatMessageCreate, current_user: User = Depends(get_current_active_user)):
    """Send a chat message"""
    try:
        # Save user message
        user_message = await ChatService.create_message(current_user.id, message_data)
        
        # Generate AI response if user message
        if message_data.message_type == MessageTypeEnum.user:
            ai_response_text = await ChatService.generate_ai_response(message_data.content)
            ai_message_data = ChatMessageCreate(
                session_id=message_data.session_id,
                message_type=MessageTypeEnum.ai,
                content=ai_response_text
            )
            await ChatService.create_message(current_user.id, ai_message_data)
        
        return user_message
    except Exception as e:
        logger.error(f"Error sending chat message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/chat/{session_id}", response_model=List[ChatMessage])
async def get_chat_messages(session_id: str, current_user: User = Depends(get_current_active_user)):
    """Get chat messages for a session"""
    try:
        return await ChatService.get_session_messages(current_user.id, session_id)
    except Exception as e:
        logger.error(f"Error getting chat messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Course endpoints
@api_router.get("/courses", response_model=List[CourseResponse])
async def get_all_courses():
    """Get all available courses"""
    try:
        return await CourseService.get_all_courses()
    except Exception as e:
        logger.error(f"Error getting courses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/courses/enrolled", response_model=List[CourseResponse])
async def get_enrolled_courses(current_user: User = Depends(get_current_active_user)):
    """Get user's enrolled courses"""
    try:
        return await CourseService.get_user_courses(current_user.id)
    except Exception as e:
        logger.error(f"Error getting enrolled courses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/courses/{course_id}/enroll", response_model=dict)
async def enroll_in_course(course_id: str, current_user: User = Depends(get_current_active_user)):
    """Enroll user in a course"""
    try:
        enrollment = await CourseService.enroll_user(current_user.id, course_id)
        return {"success": True, "message": "Successfully enrolled in course", "enrollment_id": enrollment.id}
    except Exception as e:
        logger.error(f"Error enrolling in course: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Stats endpoints
@api_router.get("/stats", response_model=UserStats)
async def get_user_stats(current_user: User = Depends(get_current_active_user)):
    """Get user statistics"""
    try:
        return await StatsService.get_user_stats(current_user.id)
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/stats/update", response_model=UserStats)
async def update_user_stats(current_user: User = Depends(get_current_active_user)):
    """Update and recalculate user statistics"""
    try:
        return await StatsService.update_user_stats(current_user.id)
    except Exception as e:
        logger.error(f"Error updating user stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Insights endpoints
@api_router.get("/insights")
async def get_insights_data(
    date_range: str = Query("all_time", regex="^(weekly|monthly|yearly|all_time)$"),
    current_user: User = Depends(get_current_active_user)
):
    """Get comprehensive insights data with date range filtering"""
    try:
        insights = await InsightsService.get_insights_data(current_user.id, date_range)
        return insights
    except Exception as e:
        logger.error(f"Error getting insights data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get insights data")

@api_router.get("/insights/areas/{area_id}")
async def get_area_drill_down(
    area_id: str,
    date_range: str = Query("all_time", regex="^(weekly|monthly|yearly|all_time)$"),
    current_user: User = Depends(get_current_active_user)
):
    """Get detailed breakdown for a specific area"""
    try:
        drill_down = await InsightsService.get_area_drill_down(current_user.id, area_id, date_range)
        return drill_down
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting area drill down: {e}")
        raise HTTPException(status_code=500, detail="Failed to get area breakdown")

@api_router.get("/insights/projects/{project_id}")
async def get_project_drill_down(
    project_id: str,
    date_range: str = Query("all_time", regex="^(weekly|monthly|yearly|all_time)$"),
    current_user: User = Depends(get_current_active_user)
):
    """Get detailed task breakdown for a specific project"""
    try:
        drill_down = await InsightsService.get_project_drill_down(current_user.id, project_id, date_range)
        return drill_down
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting project drill down: {e}")
        raise HTTPException(status_code=500, detail="Failed to get project breakdown")

# Task Reminders & Notifications endpoints
@api_router.get("/notifications/preferences", response_model=NotificationPreference)
async def get_notification_preferences(current_user: User = Depends(get_current_active_user)):
    """Get user's notification preferences"""
    try:
        prefs = await notification_service.get_user_notification_preferences(current_user.id)
        if not prefs:
            # Create default preferences if none exist
            prefs = await notification_service.create_default_notification_preferences(current_user.id)
        return prefs
    except Exception as e:
        logger.error(f"Error getting notification preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/notifications/preferences", response_model=NotificationPreference)
async def update_notification_preferences(
    preferences: NotificationPreferenceUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update user's notification preferences"""
    try:
        updated_prefs = await notification_service.update_notification_preferences(current_user.id, preferences)
        if not updated_prefs:
            raise HTTPException(status_code=404, detail="Failed to update preferences")
        return updated_prefs
    except Exception as e:
        logger.error(f"Error updating notification preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/notifications", response_model=List[dict])
async def get_browser_notifications(
    unread_only: bool = Query(False, description="Get only unread notifications"),
    current_user: User = Depends(get_current_active_user)
):
    """Get browser notifications for the user"""
    try:
        notifications = await notification_service.get_user_browser_notifications(current_user.id, unread_only)
        return notifications
    except Exception as e:
        logger.error(f"Error getting browser notifications: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/notifications/{notification_id}/read", response_model=dict)
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Mark a notification as read"""
    try:
        success = await notification_service.mark_notification_read(current_user.id, notification_id)
        if not success:
            raise HTTPException(status_code=404, detail="Notification not found")
        return {"success": True, "message": "Notification marked as read"}
    except Exception as e:
        logger.error(f"Error marking notification as read: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/notifications/mark-all-read", response_model=dict)
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_active_user)
):
    """Mark all notifications as read for the user"""
    try:
        count = await notification_service.mark_all_notifications_read(current_user.id)
        return {"success": True, "message": f"Marked {count} notifications as read", "count": count}
    except Exception as e:
        logger.error(f"Error marking all notifications as read for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark notifications as read")

@api_router.delete("/notifications/clear-all", response_model=dict)
async def clear_all_notifications(
    current_user: User = Depends(get_current_active_user)
):
    """Clear all notifications for the user"""
    try:
        count = await notification_service.clear_all_notifications(current_user.id)
        return {"success": True, "message": f"Cleared {count} notifications", "count": count}
    except Exception as e:
        logger.error(f"Error clearing all notifications for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear notifications")

@api_router.delete("/notifications/{notification_id}", response_model=dict)
async def delete_notification(
    notification_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Delete a specific notification"""
    try:
        success = await notification_service.delete_notification(current_user.id, notification_id)
        if not success:
            raise HTTPException(status_code=404, detail="Notification not found or already deleted")
        return {"success": True, "message": "Notification deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting notification {notification_id} for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete notification")

@api_router.post("/notifications/test", response_model=dict)
async def test_notification_system(current_user: User = Depends(get_current_active_user)):
    """Test notification system by sending a test notification"""
    try:
        from datetime import datetime
        
        # Schedule a test notification for immediate delivery
        reminder_id = await notification_service.schedule_task_reminder(
            user_id=current_user.id,
            task_id="test-task-id",
            notification_type=NotificationTypeEnum.task_reminder,
            scheduled_time=datetime.utcnow(),
            title="Test Notification",
            message="This is a test notification to verify the system is working correctly.",
            channels=[NotificationChannelEnum.browser, NotificationChannelEnum.email]
        )
        
        # Immediately process the notification
        sent_count = await notification_service.process_due_reminders()
        
        return {
            "success": True,
            "message": f"Test notification sent (reminder_id: {reminder_id})",
            "notifications_processed": sent_count
        }
    except Exception as e:
        logger.error(f"Error sending test notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Resource Management API Endpoints
@api_router.post("/resources", response_model=ResourceResponse)
async def create_resource(
    resource_data: ResourceCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new file resource"""
    try:
        resource = await ResourceService.create_resource(current_user.id, resource_data)
        return await ResourceService.get_resource(current_user.id, resource.id, track_access=False)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating resource: {e}")
        raise HTTPException(status_code=500, detail="Failed to create resource")

@api_router.get("/resources", response_model=List[ResourceResponse])
async def get_resources(
    category: Optional[str] = Query(None, description="Filter by category"),
    file_type: Optional[str] = Query(None, description="Filter by file type"),
    folder_path: Optional[str] = Query(None, description="Filter by folder path"),
    include_archived: bool = Query(False, description="Include archived resources"),
    search: Optional[str] = Query(None, description="Search in filename, description, and tags"),
    skip: int = Query(0, ge=0, description="Number of resources to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of resources to return"),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's resources with filtering and pagination"""
    try:
        return await ResourceService.get_user_resources(
            user_id=current_user.id,
            category=category,
            file_type=file_type,
            folder_path=folder_path,
            include_archived=include_archived,
            search_query=search,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        logger.error(f"Error getting resources: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve resources")

@api_router.get("/resources/{resource_id}", response_model=ResourceResponse)
async def get_resource(
    resource_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific resource by ID"""
    resource = await ResourceService.get_resource(current_user.id, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource

@api_router.get("/resources/{resource_id}/content")
async def get_resource_content(
    resource_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get resource file content for viewing/downloading"""
    content = await ResourceService.get_resource_content(current_user.id, resource_id)
    if not content:
        raise HTTPException(status_code=404, detail="Resource not found")
    return content

@api_router.put("/resources/{resource_id}", response_model=ResourceResponse)
async def update_resource(
    resource_id: str,
    resource_data: ResourceUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update a resource"""
    try:
        success = await ResourceService.update_resource(current_user.id, resource_id, resource_data)
        if not success:
            raise HTTPException(status_code=404, detail="Resource not found")
        
        return await ResourceService.get_resource(current_user.id, resource_id, track_access=False)
    except Exception as e:
        logger.error(f"Error updating resource: {e}")
        raise HTTPException(status_code=500, detail="Failed to update resource")

@api_router.delete("/resources/{resource_id}")
async def delete_resource(
    resource_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Delete a resource"""
    success = await ResourceService.delete_resource(current_user.id, resource_id)
    if not success:
        raise HTTPException(status_code=404, detail="Resource not found")
    return {"message": "Resource deleted successfully"}

# Resource Attachment Endpoints
@api_router.post("/resources/{resource_id}/attach")
async def attach_resource_to_entity(
    resource_id: str,
    attachment_data: EntityAttachmentRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Attach a resource to an entity"""
    try:
        success = await ResourceService.attach_resource_to_entity(
            user_id=current_user.id,
            resource_id=resource_id,
            entity_type=attachment_data.entity_type,
            entity_id=attachment_data.entity_id
        )
        if not success:
            raise HTTPException(status_code=400, detail="Failed to attach resource")
        return {"message": "Resource attached successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error attaching resource: {e}")
        raise HTTPException(status_code=500, detail="Failed to attach resource")

@api_router.delete("/resources/{resource_id}/detach")
async def detach_resource_from_entity(
    resource_id: str,
    attachment_data: EntityAttachmentRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Detach a resource from an entity"""
    try:
        success = await ResourceService.detach_resource_from_entity(
            user_id=current_user.id,
            resource_id=resource_id,
            entity_type=attachment_data.entity_type,
            entity_id=attachment_data.entity_id
        )
        return {"message": "Resource detached successfully"}
    except Exception as e:
        logger.error(f"Error detaching resource: {e}")
        raise HTTPException(status_code=500, detail="Failed to detach resource")

@api_router.get("/resources/entity/{entity_type}/{entity_id}", response_model=List[ResourceResponse])
async def get_entity_resources(
    entity_type: str,
    entity_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get all resources attached to a specific entity (legacy method)"""
    valid_entity_types = ["task", "project", "area", "pillar", "journal_entry"]
    if entity_type not in valid_entity_types:
        raise HTTPException(status_code=400, detail=f"Invalid entity type. Must be one of: {valid_entity_types}")
    
    try:
        return await ResourceService.get_entity_resources(current_user.id, entity_type, entity_id)
    except Exception as e:
        logger.error(f"Error getting entity resources: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve entity resources")

@api_router.get("/resources/parent/{parent_type}/{parent_id}", response_model=List[ResourceResponse])
async def get_parent_resources(
    parent_type: str,
    parent_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get all resources attached to a specific parent entity (contextual attachments)"""
    try:
        return await ResourceService.get_parent_resources(current_user.id, parent_type, parent_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting parent resources: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve parent resources")

from models import User
from auth import get_current_active_user
from ai_coach_service import AiCoachService

# AI Coach endpoints
@api_router.get("/ai_coach/today")
async def get_todays_priorities(
    current_user: User = Depends(get_current_active_user)
):
    """Get AI-recommended priority tasks for today"""
    try:
        priorities = await AiCoachService.get_todays_priorities(current_user.id)
        
        return {
            "success": True,
            "recommendations": priorities,
            "message": "Focus on these tasks to maximize your progress today." if priorities else "Great work! No urgent tasks today - consider working on your long-term goals.",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting today's priorities: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get today's priorities")

@api_router.post("/ai_coach/chat")
async def chat_with_ai_coach(
    message: str,
    current_user: User = Depends(get_current_active_user)
):
    """Chat with the AI Coach about your data and get personalized insights"""
    try:
        response = await AiCoachService.chat_with_coach(current_user.id, message)
        
        return {
            "success": True,
            "response": response,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in AI coach chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to chat with AI coach")

# Achievement endpoints
@api_router.get("/achievements")
async def get_user_achievements(
    current_user: User = Depends(get_current_active_user)
):
    """Get all achievements for the current user with progress"""
    try:
        achievements = await AchievementService.get_user_achievements(current_user.id)
        
        return {
            "success": True,
            "achievements": achievements,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting achievements: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get achievements")

@api_router.post("/achievements/check")
async def check_achievements(
    current_user: User = Depends(get_current_active_user)
):
    """Manually trigger achievement checking (for testing/admin)"""
    try:
        newly_unlocked = await AchievementService.check_and_unlock_achievements(current_user.id)
        
        return {
            "success": True,
            "newly_unlocked": len(newly_unlocked),
            "achievements": [{"id": badge.id, "name": badge.name, "icon": badge.icon} for badge in newly_unlocked],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error checking achievements: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to check achievements")

# Custom Achievement endpoints
@api_router.get("/achievements/custom")
async def get_custom_achievements(
    include_completed: bool = True,
    current_user: User = Depends(get_current_active_user)
):
    """Get all custom achievements for the current user"""
    try:
        custom_achievements = await CustomAchievementService.get_user_custom_achievements(
            current_user.id, include_completed
        )
        
        return {
            "success": True,
            "custom_achievements": [achievement.dict() for achievement in custom_achievements],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting custom achievements: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get custom achievements")

@api_router.post("/achievements/custom")
async def create_custom_achievement(
    achievement_data: CustomAchievementCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new custom achievement"""
    try:
        custom_achievement = await CustomAchievementService.create_custom_achievement(
            current_user.id, achievement_data
        )
        
        return {
            "success": True,
            "achievement": custom_achievement.dict(),
            "message": f"Custom achievement '{custom_achievement.name}' created successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error creating custom achievement: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@api_router.put("/achievements/custom/{achievement_id}")
async def update_custom_achievement(
    achievement_id: str,
    achievement_data: CustomAchievementUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update a custom achievement"""
    try:
        success = await CustomAchievementService.update_custom_achievement(
            current_user.id, achievement_id, achievement_data
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Custom achievement not found")
        
        return {
            "success": True,
            "message": "Custom achievement updated successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating custom achievement: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update custom achievement")

@api_router.delete("/achievements/custom/{achievement_id}")
async def delete_custom_achievement(
    achievement_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Delete a custom achievement"""
    try:
        success = await CustomAchievementService.delete_custom_achievement(
            current_user.id, achievement_id
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Custom achievement not found")
        
        return {
            "success": True,
            "message": "Custom achievement deleted successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting custom achievement: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete custom achievement")

@api_router.post("/achievements/custom/check")
async def check_custom_achievements(
    current_user: User = Depends(get_current_active_user)
):
    """Check and update progress for all custom achievements"""
    try:
        newly_completed = await CustomAchievementService.check_custom_achievements_progress(current_user.id)
        
        return {
            "success": True,
            "newly_completed": len(newly_completed),
            "achievements": [
                {"id": achievement.id, "name": achievement.name, "icon": achievement.icon} 
                for achievement in newly_completed
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error checking custom achievements: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to check custom achievements")

# Feedback and Support endpoint
@api_router.post("/feedback")
async def submit_feedback(
    feedback_data: dict,
    current_user: User = Depends(get_current_active_user)
):
    """Submit user feedback and send email to support"""
    try:
        from email_service import EmailService
        
        # Extract feedback data
        category = feedback_data.get('category', '')
        subject = feedback_data.get('subject', 'User Feedback')
        message = feedback_data.get('message', '')
        user_email = feedback_data.get('email', current_user.email)
        user_name = feedback_data.get('user_name', f"{current_user.first_name} {current_user.last_name}")
        
        # Create email content
        category_labels = {
            'suggestion': 'Feature Suggestion',
            'bug_report': 'Bug Report', 
            'general_feedback': 'General Feedback',
            'support_request': 'Support Request',
            'compliment': 'Compliment'
        }
        
        category_label = category_labels.get(category, 'Feedback')
        email_subject = f"Aurum Life - {category_label}: {subject}"
        
        email_body = f"""Hello Marc,

You've received new feedback from an Aurum Life user:

FEEDBACK TYPE: {category_label}
SUBJECT: {subject}

FROM: {user_name}
EMAIL: {user_email}
USER ID: {current_user.id}
SUBMITTED: {datetime.utcnow().strftime('%B %d, %Y at %I:%M %p UTC')}

MESSAGE:
{message}

---
You can reply directly to this email to respond to the user.
This feedback was submitted through the Aurum Life application.
        """.strip()
        
        # Send email to support
        email_service = EmailService()
        success = email_service.send_email(
            to="marc.alleyne@aurumtechnologyltd.com",
            subject=email_subject,
            html_content=email_body.replace('\n', '<br>'),
            plain_text_content=email_body
        )
        
        if not success:
            logger.error(f"Failed to send feedback email for user {current_user.id}")
            # Still return success to user since feedback was received, just email failed
        
        # Log feedback submission
        logger.info(f"Feedback submitted by user {current_user.id} ({user_email}): {category} - {subject}")
        
        return {
            "success": True,
            "message": "Feedback submitted successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit feedback")

# Include the router in the main app
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup and shutdown events
@app.on_event("startup")
async def startup_db_client():
    # Initialize Supabase connection
    try:
        supabase_client = supabase_manager.get_client()
        logger.info("✅ Supabase client initialized")
    except Exception as e:
        logger.error(f"❌ Error initializing Supabase client: {e}")
    
    # Initialize default journal templates
    try:
        await JournalService.initialize_default_templates()
        logger.info("✅ Default journal templates initialized")
    except Exception as e:
        logger.error(f"❌ Error initializing journal templates: {e}")
    
    logger.info("🚀 Aurum Life API started with Supabase")

@app.on_event("shutdown")
async def shutdown_db_client():
    logger.info("💤 Aurum Life API shutdown complete")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)