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
from database import connect_to_mongo, close_mongo_connection
from models import *
from services import *
from auth import create_access_token, get_current_active_user, ACCESS_TOKEN_EXPIRE_MINUTES

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
async def get_user(user_id: str = DEFAULT_USER_ID):
    """Get user by ID"""
    user = await UserService.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@api_router.put("/users/{user_id}", response_model=dict)
async def update_user(user_data: UserUpdate, user_id: str = DEFAULT_USER_ID):
    """Update user"""
    success = await UserService.update_user(user_id, user_data)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"success": True, "message": "User updated successfully"}

# Dashboard endpoint
@api_router.get("/dashboard", response_model=UserDashboard)
async def get_dashboard(user_id: str = Query(DEFAULT_USER_ID)):
    """Get dashboard data for user"""
    try:
        return await StatsService.get_dashboard_data(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Habit endpoints
@api_router.post("/habits", response_model=Habit)
async def create_habit(habit_data: HabitCreate, user_id: str = Query(DEFAULT_USER_ID)):
    """Create a new habit"""
    try:
        return await HabitService.create_habit(user_id, habit_data)
    except Exception as e:
        logger.error(f"Error creating habit: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/habits", response_model=List[HabitResponse])
async def get_habits(user_id: str = Query(DEFAULT_USER_ID)):
    """Get all habits for user"""
    try:
        return await HabitService.get_user_habits(user_id)
    except Exception as e:
        logger.error(f"Error getting habits: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/habits/{habit_id}", response_model=dict)
async def update_habit(habit_id: str, habit_data: HabitUpdate, user_id: str = Query(DEFAULT_USER_ID)):
    """Update a habit"""
    success = await HabitService.update_habit(habit_id, habit_data)
    if not success:
        raise HTTPException(status_code=404, detail="Habit not found")
    return {"success": True, "message": "Habit updated successfully"}

@api_router.post("/habits/{habit_id}/toggle", response_model=dict)
async def toggle_habit(habit_id: str, completion: HabitCompletion, user_id: str = Query(DEFAULT_USER_ID)):
    """Toggle habit completion"""
    success = await HabitService.toggle_habit_completion(user_id, habit_id, completion.completed)
    if not success:
        raise HTTPException(status_code=404, detail="Habit not found")
    return {"success": True, "message": "Habit completion updated"}

@api_router.delete("/habits/{habit_id}", response_model=dict)
async def delete_habit(habit_id: str, user_id: str = Query(DEFAULT_USER_ID)):
    """Delete a habit"""
    success = await HabitService.delete_habit(user_id, habit_id)
    if not success:
        raise HTTPException(status_code=404, detail="Habit not found")
    return {"success": True, "message": "Habit deleted successfully"}

# Journal endpoints
@api_router.post("/journal", response_model=JournalEntry)
async def create_journal_entry(entry_data: JournalEntryCreate, user_id: str = Query(DEFAULT_USER_ID)):
    """Create a new journal entry"""
    try:
        return await JournalService.create_entry(user_id, entry_data)
    except Exception as e:
        logger.error(f"Error creating journal entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/journal", response_model=List[JournalEntry])
async def get_journal_entries(
    user_id: str = Query(DEFAULT_USER_ID),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """Get journal entries for user"""
    try:
        return await JournalService.get_user_entries(user_id, skip, limit)
    except Exception as e:
        logger.error(f"Error getting journal entries: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/journal/{entry_id}", response_model=dict)
async def update_journal_entry(entry_id: str, entry_data: JournalEntryUpdate, user_id: str = Query(DEFAULT_USER_ID)):
    """Update a journal entry"""
    success = await JournalService.update_entry(user_id, entry_id, entry_data)
    if not success:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return {"success": True, "message": "Journal entry updated successfully"}

@api_router.delete("/journal/{entry_id}", response_model=dict)
async def delete_journal_entry(entry_id: str, user_id: str = Query(DEFAULT_USER_ID)):
    """Delete a journal entry"""
    success = await JournalService.delete_entry(user_id, entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return {"success": True, "message": "Journal entry deleted successfully"}

# Area endpoints
@api_router.post("/areas", response_model=Area)
async def create_area(area_data: AreaCreate, user_id: str = Query(DEFAULT_USER_ID)):
    """Create a new area"""
    try:
        return await AreaService.create_area(user_id, area_data)
    except Exception as e:
        logger.error(f"Error creating area: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/areas", response_model=List[AreaResponse])
async def get_areas(
    include_projects: bool = Query(False),
    user_id: str = Query(DEFAULT_USER_ID)
):
    """Get all areas for user"""
    try:
        return await AreaService.get_user_areas(user_id, include_projects)
    except Exception as e:
        logger.error(f"Error getting areas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/areas/{area_id}", response_model=AreaResponse)
async def get_area(area_id: str, user_id: str = Query(DEFAULT_USER_ID)):
    """Get area by ID with projects"""
    area = await AreaService.get_area(user_id, area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    return area

@api_router.put("/areas/{area_id}", response_model=dict)
async def update_area(area_id: str, area_data: AreaUpdate, user_id: str = Query(DEFAULT_USER_ID)):
    """Update an area"""
    success = await AreaService.update_area(user_id, area_id, area_data)
    if not success:
        raise HTTPException(status_code=404, detail="Area not found")
    return {"success": True, "message": "Area updated successfully"}

@api_router.delete("/areas/{area_id}", response_model=dict)
async def delete_area(area_id: str, user_id: str = Query(DEFAULT_USER_ID)):
    """Delete an area and all its projects/tasks"""
    success = await AreaService.delete_area(user_id, area_id)
    if not success:
        raise HTTPException(status_code=404, detail="Area not found")
    return {"success": True, "message": "Area deleted successfully"}

# Project endpoints
@api_router.post("/projects", response_model=Project)
async def create_project(project_data: ProjectCreate, user_id: str = Query(DEFAULT_USER_ID)):
    """Create a new project"""
    try:
        return await ProjectService.create_project(user_id, project_data)
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/projects", response_model=List[ProjectResponse])
async def get_projects(
    area_id: str = Query(None),
    user_id: str = Query(DEFAULT_USER_ID)
):
    """Get all projects for user, optionally filtered by area"""
    try:
        return await ProjectService.get_user_projects(user_id, area_id)
    except Exception as e:
        logger.error(f"Error getting projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str, 
    include_tasks: bool = Query(False),
    user_id: str = Query(DEFAULT_USER_ID)
):
    """Get project by ID"""
    project = await ProjectService.get_project(user_id, project_id, include_tasks)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@api_router.put("/projects/{project_id}", response_model=dict)
async def update_project(project_id: str, project_data: ProjectUpdate, user_id: str = Query(DEFAULT_USER_ID)):
    """Update a project"""
    success = await ProjectService.update_project(user_id, project_id, project_data)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"success": True, "message": "Project updated successfully"}

@api_router.delete("/projects/{project_id}", response_model=dict)
async def delete_project(project_id: str, user_id: str = Query(DEFAULT_USER_ID)):
    """Delete a project and all its tasks"""
    success = await ProjectService.delete_project(user_id, project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"success": True, "message": "Project deleted successfully"}

# Enhanced Task endpoints
@api_router.get("/projects/{project_id}/tasks", response_model=List[TaskResponse])
async def get_project_tasks(project_id: str, user_id: str = Query(DEFAULT_USER_ID)):
    """Get all tasks for a specific project"""
    try:
        return await TaskService.get_project_tasks(project_id)
    except Exception as e:
        logger.error(f"Error getting project tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/projects/{project_id}/kanban", response_model=KanbanBoard)
async def get_kanban_board(project_id: str, user_id: str = Query(DEFAULT_USER_ID)):
    """Get kanban board for a project"""
    try:
        return await TaskService.get_kanban_board(user_id, project_id)
    except Exception as e:
        logger.error(f"Error getting kanban board: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/tasks/{task_id}/column", response_model=dict)
async def move_task_column(task_id: str, new_column: str, user_id: str = Query(DEFAULT_USER_ID)):
    """Move task to different kanban column"""
    success = await TaskService.move_task_column(user_id, task_id, new_column)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid column or task not found")
    return {"success": True, "message": "Task moved successfully"}

@api_router.get("/today", response_model=TodayView)
async def get_today_view(user_id: str = Query(DEFAULT_USER_ID)):
    """Get today's focused view"""
    try:
        return await StatsService.get_today_view(user_id)
    except Exception as e:
        logger.error(f"Error getting today view: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Update existing task endpoints to work with new structure
# Task endpoints (updated for project integration)
@api_router.post("/tasks", response_model=Task)
async def create_task(task_data: TaskCreate, user_id: str = Query(DEFAULT_USER_ID)):
    """Create a new task"""
    try:
        return await TaskService.create_task(user_id, task_data)
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(
    project_id: str = Query(None),
    user_id: str = Query(DEFAULT_USER_ID)
):
    """Get all tasks for user, optionally filtered by project"""
    try:
        return await TaskService.get_user_tasks(user_id, project_id)
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/tasks/{task_id}", response_model=dict)
async def update_task(task_id: str, task_data: TaskUpdate, user_id: str = Query(DEFAULT_USER_ID)):
    """Update a task"""
    success = await TaskService.update_task(user_id, task_id, task_data)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"success": True, "message": "Task updated successfully"}

@api_router.delete("/tasks/{task_id}", response_model=dict)
async def delete_task(task_id: str, user_id: str = Query(DEFAULT_USER_ID)):
    """Delete a task"""
    success = await TaskService.delete_task(user_id, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"success": True, "message": "Task deleted successfully"}

# Chat endpoints
@api_router.post("/chat", response_model=ChatMessage)
async def send_chat_message(message_data: ChatMessageCreate, user_id: str = Query(DEFAULT_USER_ID)):
    """Send a chat message"""
    try:
        # Save user message
        user_message = await ChatService.create_message(user_id, message_data)
        
        # Generate AI response if user message
        if message_data.message_type == MessageTypeEnum.user:
            ai_response_text = await ChatService.generate_ai_response(message_data.content)
            ai_message_data = ChatMessageCreate(
                session_id=message_data.session_id,
                message_type=MessageTypeEnum.ai,
                content=ai_response_text
            )
            await ChatService.create_message(user_id, ai_message_data)
        
        return user_message
    except Exception as e:
        logger.error(f"Error sending chat message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/chat/{session_id}", response_model=List[ChatMessage])
async def get_chat_messages(session_id: str, user_id: str = Query(DEFAULT_USER_ID)):
    """Get chat messages for a session"""
    try:
        return await ChatService.get_session_messages(user_id, session_id)
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
async def get_enrolled_courses(user_id: str = Query(DEFAULT_USER_ID)):
    """Get user's enrolled courses"""
    try:
        return await CourseService.get_user_courses(user_id)
    except Exception as e:
        logger.error(f"Error getting enrolled courses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/courses/{course_id}/enroll", response_model=dict)
async def enroll_in_course(course_id: str, user_id: str = Query(DEFAULT_USER_ID)):
    """Enroll user in a course"""
    try:
        enrollment = await CourseService.enroll_user(user_id, course_id)
        return {"success": True, "message": "Successfully enrolled in course", "enrollment_id": enrollment.id}
    except Exception as e:
        logger.error(f"Error enrolling in course: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Stats endpoints
@api_router.get("/stats", response_model=UserStats)
async def get_user_stats(user_id: str = Query(DEFAULT_USER_ID)):
    """Get user statistics"""
    try:
        return await StatsService.get_user_stats(user_id)
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/stats/update", response_model=UserStats)
async def update_user_stats(user_id: str = Query(DEFAULT_USER_ID)):
    """Update and recalculate user statistics"""
    try:
        return await StatsService.update_user_stats(user_id)
    except Exception as e:
        logger.error(f"Error updating user stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
    await connect_to_mongo()
    logger.info("🚀 Aurum Life API started successfully")

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()
    logger.info("💤 Aurum Life API shutdown complete")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)