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
    todo = "todo"
    in_progress = "in_progress"
    review = "review"
    completed = "completed"

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
    custom = "custom"  # For flexible patterns like "every Mon/Wed"

class WeekdayEnum(str, Enum):
    monday = "monday"
    tuesday = "tuesday"
    wednesday = "wednesday"
    thursday = "thursday"
    friday = "friday"
    saturday = "saturday"
    sunday = "sunday"

# Enhanced Recurrence Models
class RecurrencePattern(BaseModel):
    """Flexible recurrence pattern configuration"""
    type: RecurrenceEnum = RecurrenceEnum.none
    interval: int = 1  # Every X days/weeks/months
    weekdays: Optional[List[WeekdayEnum]] = None  # For weekly: specific days (e.g., Mon/Wed/Fri)
    month_day: Optional[int] = None  # For monthly: specific day of month (1-31)
    end_date: Optional[datetime] = None  # When to stop creating instances
    max_instances: Optional[int] = None  # Maximum number of instances to create

class RecurringTaskTemplate(BaseDocument):
    """Template for recurring tasks - stores the pattern and task details"""
    user_id: str
    name: str
    description: str = ""
    priority: PriorityEnum = PriorityEnum.medium
    project_id: str
    category: str = "general"
    estimated_duration: Optional[int] = None
    
    # Recurrence configuration
    recurrence_pattern: RecurrencePattern
    
    # Template settings
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_generated: Optional[datetime] = None  # Last time instances were created
    next_due: Optional[datetime] = None  # Next scheduled instance

class RecurringTaskInstance(BaseDocument):
    """Individual instance of a recurring task"""
    user_id: str
    template_id: str  # Reference to RecurringTaskTemplate
    name: str
    description: str = ""
    priority: PriorityEnum = PriorityEnum.medium
    project_id: str
    category: str = "general"
    estimated_duration: Optional[int] = None
    
    # Instance-specific fields
    due_date: datetime
    due_time: Optional[str] = None
    completed: bool = False
    completed_at: Optional[datetime] = None
    skipped: bool = False  # User can skip individual instances
    
    # Task behavior
    status: TaskStatusEnum = TaskStatusEnum.todo
    kanban_column: str = "to_do"
    sort_order: int = 0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RecurringTaskCreate(BaseModel):
    name: str
    description: str = ""
    priority: PriorityEnum = PriorityEnum.medium
    project_id: str
    category: str = "general"
    estimated_duration: Optional[int] = None
    recurrence_pattern: RecurrencePattern
    due_time: Optional[str] = None  # Default time for instances

class RecurringTaskUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[PriorityEnum] = None
    category: Optional[str] = None
    estimated_duration: Optional[int] = None
    recurrence_pattern: Optional[RecurrencePattern] = None
    is_active: Optional[bool] = None
    due_time: Optional[str] = None

class RecurringTaskResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: str
    priority: PriorityEnum
    project_id: str
    project_name: Optional[str] = None
    category: str
    estimated_duration: Optional[int] = None
    recurrence_pattern: RecurrencePattern
    is_active: bool
    created_at: datetime
    last_generated: Optional[datetime] = None
    next_due: Optional[datetime] = None
    due_time: Optional[str] = None
    
    # Statistics
    total_instances: int = 0
    completed_instances: int = 0
    completion_rate: float = 0.0
class Area(BaseDocument):
    user_id: str
    pillar_id: Optional[str] = None  # Link to parent pillar
    name: str
    description: str = ""
    icon: str = "🎯"
    color: str = "#F4B400"
    archived: bool = False
    sort_order: int = 0

class AreaCreate(BaseModel):
    pillar_id: Optional[str] = None
    name: str
    description: str = ""
    icon: str = "🎯"
    color: str = "#F4B400"

class AreaUpdate(BaseModel):
    pillar_id: Optional[str] = None
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
    archived: bool = False
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
    status: TaskStatusEnum = TaskStatusEnum.todo
    priority: PriorityEnum = PriorityEnum.medium
    due_date: Optional[datetime] = None
    due_time: Optional[str] = None  # Time in HH:MM format (e.g., "14:30")
    reminder_date: Optional[datetime] = None
    category: str = "general"
    completed: bool = False
    completed_at: Optional[datetime] = None
    dependency_task_ids: List[str] = []  # Tasks that must be completed first
    recurrence: RecurrenceEnum = RecurrenceEnum.none
    recurrence_interval: int = 1
    next_due_date: Optional[datetime] = None
    kanban_column: str = "to_do"  # to_do, in_progress, review, done
    sort_order: int = 0
    estimated_duration: Optional[int] = None  # in minutes
    # Sub-task completion tracking
    sub_task_completion_required: bool = False  # If true, main task complete only when all sub-tasks complete

class TaskCreate(BaseModel):
    project_id: str
    parent_task_id: Optional[str] = None
    name: str
    description: str = ""
    status: TaskStatusEnum = TaskStatusEnum.todo
    priority: PriorityEnum = PriorityEnum.medium
    due_date: Optional[datetime] = None
    due_time: Optional[str] = None  # Time in HH:MM format
    reminder_date: Optional[datetime] = None
    category: str = "general"
    dependency_task_ids: List[str] = []
    recurrence: RecurrenceEnum = RecurrenceEnum.none
    recurrence_interval: int = 1
    estimated_duration: Optional[int] = None
    sub_task_completion_required: bool = False

class TaskUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatusEnum] = None
    priority: Optional[PriorityEnum] = None
    due_date: Optional[datetime] = None
    due_time: Optional[str] = None  # Time in HH:MM format
    reminder_date: Optional[datetime] = None
    category: Optional[str] = None
    completed: Optional[bool] = None
    dependency_task_ids: Optional[List[str]] = None
    recurrence: Optional[RecurrenceEnum] = None
    recurrence_interval: Optional[int] = None
    kanban_column: Optional[str] = None
    sort_order: Optional[int] = None
    estimated_duration: Optional[int] = None
    sub_task_completion_required: Optional[bool] = None

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
    active_task_count: Optional[int] = None
    completion_percentage: Optional[float] = None
    area_name: Optional[str] = None
    is_overdue: Optional[bool] = None
    archived: bool = False
    tasks: Optional[List[TaskResponse]] = []

class AreaResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    color: str
    icon: str
    user_id: str
    pillar_id: Optional[str] = None
    pillar_name: Optional[str] = None  # For display purposes
    sort_order: int = 0
    archived: bool = False
    created_at: datetime
    updated_at: datetime
    project_count: int = 0
    completed_project_count: int = 0
    total_task_count: int = 0
    completed_task_count: int = 0
    projects: Optional[List['ProjectResponse']] = None

class CourseResponse(Course):
    progress_percentage: Optional[int] = None
    is_enrolled: Optional[bool] = None

class UserDashboard(BaseModel):
    user: User
    stats: UserStats
    recent_tasks: List[TaskResponse]
    recent_courses: List[CourseResponse]
    recent_achievements: List[UserBadge]
    areas: List[AreaResponse]
    today_tasks: List[TaskResponse]

# Daily Task Curation Models
class DailyTask(BaseDocument):
    user_id: str
    task_id: str
    date: datetime  # The date this task was added to daily view
    sort_order: int = 0
    added_at: datetime = Field(default_factory=datetime.utcnow)

class DailyTaskCreate(BaseModel):
    task_id: str
    date: Optional[datetime] = None  # Defaults to today

class DailyTasksUpdate(BaseModel):
    task_ids: List[str]  # Reorder tasks for today

# Enhanced Today View Models
class TodayView(BaseModel):
    date: datetime
    tasks: List[TaskResponse]  # Curated daily tasks
    available_tasks: List[TaskResponse]  # Tasks available to add to today
    total_tasks: int
    completed_tasks: int
    estimated_duration: int  # Total estimated time in minutes
    pomodoro_sessions: int = 0  # Number of completed pomodoro sessions today

class KanbanBoard(BaseModel):
    project_id: str
    project_name: str
    columns: Dict[str, List[TaskResponse]]

class CalendarEvent(BaseModel):
    id: str
    title: str
    type: str  # "task", "project_deadline"
    date: datetime
    priority: Optional[str] = None
    project_name: Optional[str] = None
    area_name: Optional[str] = None


# Pillar Hierarchy Models
class Pillar(BaseDocument):
    user_id: str
    name: str
    description: str = ""
    icon: str = "🎯"
    color: str = "#F4B400"
    parent_pillar_id: Optional[str] = None  # For nested pillars
    sort_order: int = 0
    archived: bool = False
    time_allocation_percentage: Optional[float] = None  # % of time/focus allocated to this pillar

class PillarCreate(BaseModel):
    name: str
    description: str = ""
    icon: str = "🎯"  
    color: str = "#F4B400"
    parent_pillar_id: Optional[str] = None
    time_allocation_percentage: Optional[float] = None

class PillarUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    parent_pillar_id: Optional[str] = None
    sort_order: Optional[int] = None
    time_allocation_percentage: Optional[float] = None

class PillarResponse(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    color: str
    user_id: str
    parent_pillar_id: Optional[str] = None
    sort_order: int = 0
    archived: bool = False
    time_allocation_percentage: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    
    # Hierarchy tracking
    sub_pillars: Optional[List['PillarResponse']] = []
    parent_pillar_name: Optional[str] = None
    
    # Progress tracking
    area_count: int = 0
    project_count: int = 0
    task_count: int = 0
    completed_task_count: int = 0
    progress_percentage: float = 0.0
    
    # Linked areas for visualization
    areas: Optional[List['AreaResponse']] = None

# Enable forward references
TaskResponse.model_rebuild()
ProjectResponse.model_rebuild()
AreaResponse.model_rebuild()
PillarResponse.model_rebuild()