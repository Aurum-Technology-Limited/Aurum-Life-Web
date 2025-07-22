from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
import uuid

# Base model for common fields
class BaseDocument(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# User models
class User(BaseDocument):
    username: str
    email: str
    first_name: str = ""
    last_name: str = ""
    password_hash: Optional[str] = None  # Make optional for backward compatibility
    is_active: bool = True
    level: int = 1
    total_points: int = 0
    current_streak: int = 0
    profile_data: Dict[str, Any] = {}

class UserCreate(BaseModel):
    username: str
    email: str
    first_name: str = ""
    last_name: str = ""
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    level: Optional[int] = None
    total_points: Optional[int] = None
    current_streak: Optional[int] = None
    profile_data: Optional[Dict[str, Any]] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    first_name: str
    last_name: str
    is_active: bool
    level: int
    total_points: int
    current_streak: int
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None

# Password Reset Models
class PasswordResetToken(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    token: str
    expires_at: datetime
    is_used: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PasswordResetRequest(BaseModel):
    email: str

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

class PasswordResetResponse(BaseModel):
    message: str
    success: bool

# Habit models
class Habit(BaseDocument):
    user_id: str
    name: str
    description: str = ""
    category: str = "health"
    target_days: int = 30
    current_streak: int = 0
    total_completed: int = 0
    is_completed_today: bool = False
    last_completed_date: Optional[datetime] = None
    color: str = "#F4B400"

class HabitCreate(BaseModel):
    name: str
    description: str = ""
    category: str = "health"
    target_days: int = 30
    color: str = "#F4B400"

class HabitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    target_days: Optional[int] = None
    color: Optional[str] = None

class HabitCompletion(BaseModel):
    habit_id: str
    completed: bool

# Journal models
class MoodEnum(str, Enum):
    optimistic = "optimistic"
    inspired = "inspired"
    reflective = "reflective"
    challenging = "challenging"

class JournalEntry(BaseDocument):
    user_id: str
    title: str
    content: str
    mood: MoodEnum = MoodEnum.reflective
    tags: List[str] = []

class JournalEntryCreate(BaseModel):
    title: str
    content: str
    mood: MoodEnum = MoodEnum.reflective
    tags: List[str] = []

class JournalEntryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    mood: Optional[MoodEnum] = None
    tags: Optional[List[str]] = None

# Task models
class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class TaskStatusEnum(str, Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"
    on_hold = "on_hold"

class ProjectStatusEnum(str, Enum):
    not_started = "Not Started"
    in_progress = "In Progress" 
    completed = "Completed"
    on_hold = "On Hold"

class RecurrenceEnum(str, Enum):
    none = "none"
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"

# Area models
class Area(BaseDocument):
    user_id: str
    name: str
    description: str = ""
    icon: str = "🎯"
    color: str = "#F4B400"
    sort_order: int = 0

class AreaCreate(BaseModel):
    name: str
    description: str = ""
    icon: str = "🎯"
    color: str = "#F4B400"

class AreaUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    sort_order: Optional[int] = None

# Project models
class Project(BaseDocument):
    user_id: str
    area_id: str
    name: str
    description: str = ""
    deadline: Optional[datetime] = None
    status: ProjectStatusEnum = ProjectStatusEnum.not_started
    priority: PriorityEnum = PriorityEnum.medium
    completion_percentage: float = 0.0
    sort_order: int = 0

class ProjectCreate(BaseModel):
    area_id: str
    name: str
    description: str = ""
    deadline: Optional[datetime] = None
    status: ProjectStatusEnum = ProjectStatusEnum.not_started
    priority: PriorityEnum = PriorityEnum.medium

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    status: Optional[ProjectStatusEnum] = None
    priority: Optional[PriorityEnum] = None
    sort_order: Optional[int] = None

# Enhanced Task models
class Task(BaseDocument):
    user_id: str
    project_id: str
    parent_task_id: Optional[str] = None  # For sub-tasks
    name: str
    description: str = ""
    status: TaskStatusEnum = TaskStatusEnum.not_started
    priority: PriorityEnum = PriorityEnum.medium
    due_date: Optional[datetime] = None
    reminder_date: Optional[datetime] = None
    category: str = "general"
    completed: bool = False
    completed_at: Optional[datetime] = None
    dependency_task_ids: List[str] = []  # Tasks that must be completed first
    recurrence: RecurrenceEnum = RecurrenceEnum.none
    recurrence_interval: int = 1
    next_due_date: Optional[datetime] = None
    kanban_column: str = "to_do"  # to_do, in_progress, done
    sort_order: int = 0
    estimated_duration: Optional[int] = None  # in minutes

class TaskCreate(BaseModel):
    project_id: str
    parent_task_id: Optional[str] = None
    name: str
    description: str = ""
    status: TaskStatusEnum = TaskStatusEnum.not_started
    priority: PriorityEnum = PriorityEnum.medium
    due_date: Optional[datetime] = None
    reminder_date: Optional[datetime] = None
    category: str = "general"
    dependency_task_ids: List[str] = []
    recurrence: RecurrenceEnum = RecurrenceEnum.none
    recurrence_interval: int = 1
    estimated_duration: Optional[int] = None

class TaskUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatusEnum] = None
    priority: Optional[PriorityEnum] = None
    due_date: Optional[datetime] = None
    reminder_date: Optional[datetime] = None
    category: Optional[str] = None
    completed: Optional[bool] = None
    dependency_task_ids: Optional[List[str]] = None
    recurrence: Optional[RecurrenceEnum] = None
    recurrence_interval: Optional[int] = None
    kanban_column: Optional[str] = None
    sort_order: Optional[int] = None
    estimated_duration: Optional[int] = None

# Course models
class Course(BaseDocument):
    title: str
    description: str
    instructor: str
    duration: str
    category: str
    image_url: str
    lessons: List[Dict[str, Any]] = []

class UserCourseProgress(BaseDocument):
    user_id: str
    course_id: str
    progress_percentage: int = 0
    completed_lessons: List[str] = []
    enrolled_at: datetime = Field(default_factory=datetime.utcnow)
    last_accessed: Optional[datetime] = None

class CourseEnrollment(BaseModel):
    course_id: str

# Chat models
class MessageTypeEnum(str, Enum):
    user = "user"
    ai = "ai"

class ChatMessage(BaseDocument):
    user_id: str
    session_id: str
    message_type: MessageTypeEnum
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatMessageCreate(BaseModel):
    session_id: str
    message_type: MessageTypeEnum
    content: str

# Achievement models
class RarityEnum(str, Enum):
    bronze = "bronze"
    silver = "silver"
    gold = "gold"

class Badge(BaseDocument):
    name: str
    description: str
    icon: str
    rarity: RarityEnum
    category: str
    requirements: Dict[str, Any] = {}

class UserBadge(BaseDocument):
    user_id: str
    badge_id: str
    earned: bool = False
    earned_date: Optional[datetime] = None
    progress: int = 0

# Stats models
class UserStats(BaseDocument):
    user_id: str
    total_habits: int = 0
    habits_completed_today: int = 0
    total_journal_entries: int = 0
    total_tasks: int = 0
    tasks_completed: int = 0
    total_areas: int = 0
    total_projects: int = 0
    completed_projects: int = 0
    courses_enrolled: int = 0
    courses_completed: int = 0
    badges_earned: int = 0
    meditation_sessions: int = 0
    meditation_minutes: int = 0
    last_updated: datetime = Field(default_factory=datetime.utcnow)

# Project Template Models
class TaskTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    priority: PriorityEnum = PriorityEnum.medium
    estimated_duration: Optional[int] = None  # in minutes

class TaskTemplate(BaseDocument):
    name: str
    description: Optional[str] = None
    priority: PriorityEnum = PriorityEnum.medium
    estimated_duration: Optional[int] = None  # in minutes
    template_id: str  # Reference to parent project template
    sort_order: int = 0

class ProjectTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    tasks: List[TaskTemplateCreate] = []

class ProjectTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tasks: Optional[List[TaskTemplateCreate]] = None

class ProjectTemplate(BaseDocument):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    user_id: str
    usage_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProjectTemplateResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    user_id: str
    usage_count: int = 0
    task_count: int = 0
    tasks: List[TaskTemplate] = []
    created_at: datetime
    updated_at: datetime

# Response Models for Frontend
class TaskResponse(Task):
    is_overdue: Optional[bool] = None
    can_start: Optional[bool] = None  # Based on dependencies
    sub_tasks: Optional[List['TaskResponse']] = []
    dependency_tasks: Optional[List['TaskResponse']] = []

class ProjectResponse(Project):
    task_count: Optional[int] = None
    completed_task_count: Optional[int] = None
    area_name: Optional[str] = None
    is_overdue: Optional[bool] = None
    tasks: Optional[List[TaskResponse]] = []

class AreaResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    color: str
    icon: str
    user_id: str
    sort_order: int = 0
    archived: bool = False
    created_at: datetime
    updated_at: datetime
    project_count: int = 0
    completed_project_count: int = 0
    total_task_count: int = 0
    completed_task_count: int = 0
    projects: Optional[List['ProjectResponse']] = None

class HabitResponse(Habit):
    progress_percentage: Optional[float] = None

class CourseResponse(Course):
    progress_percentage: Optional[int] = None
    is_enrolled: Optional[bool] = None

class UserDashboard(BaseModel):
    user: User
    stats: UserStats
    recent_habits: List[HabitResponse]
    recent_tasks: List[TaskResponse]
    recent_courses: List[CourseResponse]
    recent_achievements: List[UserBadge]
    areas: List[AreaResponse]
    today_tasks: List[TaskResponse]

class TodayView(BaseModel):
    date: datetime
    tasks: List[TaskResponse]
    habits: List[HabitResponse]
    total_tasks: int
    completed_tasks: int
    estimated_duration: int  # Total estimated time in minutes

class KanbanBoard(BaseModel):
    project_id: str
    project_name: str
    columns: Dict[str, List[TaskResponse]]

class CalendarEvent(BaseModel):
    id: str
    title: str
    type: str  # "task", "habit", "project_deadline"
    date: datetime
    priority: Optional[str] = None
    project_name: Optional[str] = None
    area_name: Optional[str] = None

# Enable forward references
TaskResponse.model_rebuild()
ProjectResponse.model_rebuild()
AreaResponse.model_rebuild()