from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import date, datetime, timezone
from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from enum import Enum
import uuid

# Base model for common fields
class BaseDocument(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# User models
class User(BaseDocument):
    email: str
    username: str  # Mandatory field
    password_hash: Optional[str] = None  # Optional for Google OAuth users
    first_name: str  # Mandatory field
    last_name: str  # Mandatory field
    google_id: Optional[str] = None  # Google OAuth ID
    profile_picture: Optional[str] = None  # URL to profile picture
    is_active: bool = True
    has_completed_onboarding: bool = False  # Flag to track onboarding completion
    profile_data: Optional[Dict[str, Any]] = None  # JSON field for additional profile data
    last_username_change: Optional[datetime] = None  # Track last username change for rate limiting

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
    has_completed_onboarding: bool = False  # Default to False if not present
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None

class UserProfileUpdate(BaseModel):
    first_name: str  # Mandatory field
    last_name: str  # Mandatory field
    username: str  # Mandatory field
    
    @validator('first_name', 'last_name', 'username')
    def validate_non_empty_strings(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip()

# Username change tracking model
class UsernameChangeRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    old_username: str
    new_username: str
    changed_at: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None

class AccountDeletionConfirmation(BaseModel):
    """Model for account deletion confirmation"""
    confirmation_text: str
    
    @validator('confirmation_text')
    def validate_confirmation_text(cls, v):
        if v != 'DELETE':
            raise ValueError('Confirmation text must be exactly "DELETE"')
        return v

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

# Google OAuth models
class GoogleAuthRequest(BaseModel):
    token: str  # Google ID token

class GoogleAuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: 'User'

# Enhanced Journal models with templates and advanced features
class MoodEnum(str, Enum):
    optimistic = "optimistic"
    inspired = "inspired"
    reflective = "reflective"
    challenging = "challenging"
    anxious = "anxious"
    grateful = "grateful"
    excited = "excited"
    frustrated = "frustrated"
    peaceful = "peaceful"
    motivated = "motivated"

class EnergyLevelEnum(str, Enum):
    very_low = "very_low"     # 1
    low = "low"               # 2
    moderate = "moderate"     # 3
    high = "high"             # 4
    very_high = "very_high"   # 5

class JournalTemplateTypeEnum(str, Enum):
    daily_reflection = "daily_reflection"
    gratitude = "gratitude"
    goal_setting = "goal_setting"
    weekly_review = "weekly_review"
    mood_tracker = "mood_tracker"
    learning_log = "learning_log"
    creative_writing = "creative_writing"
    problem_solving = "problem_solving"
    habit_tracker = "habit_tracker"
    custom = "custom"

class JournalTemplate(BaseDocument):
    user_id: str
    name: str
    description: str = ""
    template_type: JournalTemplateTypeEnum
    prompts: List[str] = []  # Guided prompts for the template
    default_tags: List[str] = []
    is_default: bool = False  # System templates vs user-created
    usage_count: int = 0
    icon: str = "📝"
    color: str = "#F4B400"

class JournalTemplateCreate(BaseModel):
    name: str
    description: str = ""
    template_type: JournalTemplateTypeEnum
    prompts: List[str] = []
    default_tags: List[str] = []
    icon: str = "📝"
    color: str = "#F4B400"

class JournalTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    prompts: Optional[List[str]] = None
    default_tags: Optional[List[str]] = None
    icon: Optional[str] = None
    color: Optional[str] = None

class JournalEntry(BaseDocument):
    user_id: str
    title: str
    content: str
    mood: MoodEnum = MoodEnum.reflective
    energy_level: EnergyLevelEnum = EnergyLevelEnum.moderate
    tags: List[str] = []
    template_id: Optional[str] = None  # Reference to template used
    template_responses: Dict[str, str] = {}  # Responses to template prompts
    weather: Optional[str] = None  # Optional weather note
    location: Optional[str] = None  # Optional location
    word_count: int = 0
    reading_time_minutes: int = 0
    deleted: bool = False
    deleted_at: Optional[datetime] = None

class JournalEntryCreate(BaseModel):
    title: str
    content: str
    mood: MoodEnum = MoodEnum.reflective
    energy_level: EnergyLevelEnum = EnergyLevelEnum.moderate
    tags: List[str] = []
    template_id: Optional[str] = None
    template_responses: Dict[str, str] = {}
    weather: Optional[str] = None
    location: Optional[str] = None

class JournalEntryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    mood: Optional[MoodEnum] = None
    energy_level: Optional[EnergyLevelEnum] = None
    tags: Optional[List[str]] = None
    template_responses: Optional[Dict[str, str]] = None
    weather: Optional[str] = None
    location: Optional[str] = None

class JournalEntryResponse(BaseModel):
    id: str
    user_id: str
    title: str
    content: str
    mood: MoodEnum
    energy_level: EnergyLevelEnum
    tags: List[str]
    template_id: Optional[str]
    template_name: Optional[str]
    template_responses: Dict[str, str]
    weather: Optional[str]
    location: Optional[str]
    word_count: int
    reading_time_minutes: int
    created_at: datetime
    updated_at: datetime

class JournalInsights(BaseModel):
    total_entries: int
    current_streak: int
    most_common_mood: str
    average_energy_level: float
    most_used_tags: List[Dict[str, Any]]
    mood_trend: List[Dict[str, Any]]  # Last 30 days
    energy_trend: List[Dict[str, Any]]  # Last 30 days
    writing_stats: Dict[str, Any]
    
class OnThisDayEntry(BaseModel):
    entry: JournalEntryResponse
    years_ago: int

# Task models
class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class ImportanceEnum(int, Enum):
    low = 1
    medium_low = 2
    medium = 3
    medium_high = 4
    critical = 5

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
    importance: ImportanceEnum = ImportanceEnum.medium  # New importance field
    archived: bool = False
    sort_order: int = 0
    date_created: datetime = Field(default_factory=datetime.utcnow)

class AreaCreate(BaseModel):
    pillar_id: str
    name: str
    description: str = ""
    icon: str = "🎯"
    color: str = "#F4B400"
    importance: ImportanceEnum = ImportanceEnum.medium

class AreaUpdate(BaseModel):
    pillar_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    importance: Optional[Union[ImportanceEnum, int]] = None  # Allow both enum and int
    sort_order: Optional[int] = None
    
    @validator('importance', pre=True)
    def validate_importance(cls, v):
        if v is None:
            return v
        if isinstance(v, int):
            # Convert int to ImportanceEnum if valid
            if v in [1, 2, 3, 4, 5]:
                return ImportanceEnum(v)
            else:
                raise ValueError("Importance must be between 1 and 5")
        return v

# Project models
class Project(BaseDocument):
    user_id: str
    area_id: str
    name: str
    description: str = ""
    icon: str = "🚀"  # Add icon field for projects
    deadline: Optional[datetime] = None
    status: ProjectStatusEnum = ProjectStatusEnum.not_started
    priority: PriorityEnum = PriorityEnum.medium
    importance: ImportanceEnum = ImportanceEnum.medium  # New importance field
    completion_percentage: float = 0.0
    archived: bool = False
    sort_order: int = 0
    date_created: datetime = Field(default_factory=datetime.utcnow)

class ProjectCreate(BaseModel):
    area_id: str
    name: str
    description: str = ""
    icon: str = "🚀"  # Add icon field
    deadline: Optional[datetime] = None
    status: ProjectStatusEnum = ProjectStatusEnum.not_started
    priority: PriorityEnum = PriorityEnum.medium
    importance: ImportanceEnum = ImportanceEnum.medium

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None  # Add icon field
    deadline: Optional[datetime] = None
    status: Optional[ProjectStatusEnum] = None
    priority: Optional[PriorityEnum] = None
    importance: Optional[ImportanceEnum] = None
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
    # Legacy recurrence fields (maintained for backward compatibility)
    recurrence: RecurrenceEnum = RecurrenceEnum.none
    recurrence_interval: int = 1
    # New enhanced recurrence pattern
    recurrence_pattern: Optional[RecurrencePattern] = None
    next_due_date: Optional[datetime] = None
    kanban_column: str = "to_do"  # to_do, in_progress, review, done
    sort_order: int = 0
    estimated_duration: Optional[int] = None  # in minutes
    # Sub-task completion tracking
    sub_task_completion_required: bool = False  # If true, main task complete only when all sub-tasks complete
    date_created: datetime = Field(default_factory=datetime.utcnow)

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
    # Legacy recurrence fields (maintained for backward compatibility)
    recurrence: RecurrenceEnum = RecurrenceEnum.none
    recurrence_interval: int = 1
    # New enhanced recurrence pattern
    recurrence_pattern: Optional[RecurrencePattern] = None
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
    # Legacy recurrence fields (maintained for backward compatibility)
    recurrence: Optional[RecurrenceEnum] = None
    recurrence_interval: Optional[int] = None
    # New enhanced recurrence pattern
    recurrence_pattern: Optional[RecurrencePattern] = None
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
class TaskResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    completed: bool = False
    
    # Priority and scheduling
    priority: Optional[PriorityEnum] = PriorityEnum.medium
    due_date: Optional[datetime] = None
    scheduled_date: Optional[date] = None
    
    # Hierarchy relationships
    project_id: Optional[str] = None
    area_id: Optional[str] = None
    pillar_id: Optional[str] = None
    
    # Task relationships
    parent_task_id: Optional[str] = None
    dependency_task_ids: List[str] = []
    sub_tasks: List['TaskResponse'] = []
    dependency_tasks: List['TaskResponse'] = []
    
    # Progress tracking
    progress_percentage: int = 0
    time_logged: int = 0  # in minutes
    estimated_time: Optional[int] = None  # in minutes
    
    # Kanban and organization
    kanban_column: Optional[str] = "to_do"
    sort_order: int = 0
    status: Optional[TaskStatusEnum] = TaskStatusEnum.todo
    
    # Behavioral flags
    is_recurring: bool = False
    recurring_pattern: Optional[str] = None
    is_overdue: bool = False
    can_start: bool = True
    
    # Attachments and notes
    attachments: List[dict] = []
    notes: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 🚀 THE ARCHITECT'S SCORING SYSTEM - PHASE 2 IMPLEMENTATION
    current_score: float = 0.0  # The pre-calculated priority score (0-100)
    score_last_updated: datetime = Field(default_factory=datetime.utcnow)
    score_calculation_version: int = 1  # For future algorithm updates
    
    # 🚀 DENORMALIZED HIERARCHY DATA - Eliminates real-time lookups
    area_importance: int = 3  # Cached from parent area (1-5 scale)
    project_importance: int = 3  # Cached from parent project (1-5 scale) 
    pillar_weight: float = 1.0  # Cached from root pillar (0.1-2.0 scale)
    dependencies_met: bool = True  # Pre-calculated dependency status

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
    date_created: datetime
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
    sort_order: int = 0
    archived: bool = False
    time_allocation_percentage: Optional[float] = None  # % of time/focus allocated to this pillar
    date_created: datetime = Field(default_factory=datetime.utcnow)

class PillarCreate(BaseModel):
    name: str
    description: str = ""
    icon: str = "🎯"  
    color: str = "#F4B400"
    time_allocation_percentage: Optional[float] = None

class PillarUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    sort_order: Optional[int] = None
    time_allocation_percentage: Optional[float] = None

class PillarResponse(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    color: str
    user_id: str
    sort_order: int = 0
    archived: bool = False
    time_allocation_percentage: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    date_created: datetime
    
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

# AI Coach MVP Feature Models
class DailyReflection(BaseDocument):
    """Daily reflection entry for habit formation and progress tracking"""
    user_id: str
    reflection_date: datetime = Field(default_factory=lambda: datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0))
    reflection_text: str
    completion_score: Optional[int] = None  # 1-10 scale
    mood: Optional[str] = None
    biggest_accomplishment: Optional[str] = None
    challenges_faced: Optional[str] = None
    tomorrow_focus: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DailyReflectionCreate(BaseModel):
    reflection_text: str
    completion_score: Optional[int] = None
    mood: Optional[str] = None
    biggest_accomplishment: Optional[str] = None
    challenges_faced: Optional[str] = None
    tomorrow_focus: Optional[str] = None
    reflection_date: Optional[datetime] = None

class DailyReflectionResponse(BaseModel):
    id: str
    user_id: str
    reflection_date: datetime
    reflection_text: str
    completion_score: Optional[int]
    mood: Optional[str]
    biggest_accomplishment: Optional[str]
    challenges_faced: Optional[str]
    tomorrow_focus: Optional[str]
    created_at: datetime

class ProjectDecompositionTemplate(BaseModel):
    """Template for project decomposition suggestions"""
    template_type: str
    suggested_tasks: List[Dict[str, Any]]

class ProjectDecompositionRequest(BaseModel):
    """Request for project decomposition assistance"""
    project_name: str
    project_description: Optional[str] = None
    template_type: Optional[str] = "general"

class ProjectDecompositionResponse(BaseModel):
    """Response with suggested tasks for project decomposition"""
    project_name: str
    template_type: str
    suggested_tasks: List[Dict[str, Any]]
    total_tasks: int = 0
    
class TaskWhyStatement(BaseModel):
    """Contextual why statement for a task"""
    task_id: str
    task_name: str
    why_statement: str
    pillar_connection: Optional[str] = None
    area_connection: Optional[str] = None
    project_connection: Optional[str] = None
    hrm_enhancement: Optional[Dict[str, Any]] = None  # HRM insights

class TaskWhyStatementResponse(BaseModel):
    """Response containing contextual why statements for tasks"""
    why_statements: List[TaskWhyStatement]
    tasks_analyzed: int = 0
    vertical_alignment: Dict[str, Any] = {}
    generated_at: datetime = Field(default_factory=datetime.utcnow)

# User streak tracking extension
class UserStreakUpdate(BaseModel):
    """Update user's daily streak"""
    daily_streak: int

# Task Reminders & Notifications Models
class NotificationTypeEnum(str, Enum):
    task_due = "task_due"
    task_overdue = "task_overdue"
    task_reminder = "task_reminder"
    project_deadline = "project_deadline"
    recurring_task = "recurring_task"
    achievement_unlocked = "achievement_unlocked"
    unblocked_task = "unblocked_task"

class NotificationChannelEnum(str, Enum):
    browser = "browser"
    email = "email"
    both = "both"

# Browser Notification Models
class BrowserNotification(BaseDocument):
    """Browser notification for real-time notifications"""
    user_id: str
    type: NotificationTypeEnum
    title: str
    message: str
    
    # Related entity information
    related_task_id: Optional[str] = None
    related_project_id: Optional[str] = None
    related_area_id: Optional[str] = None
    related_pillar_id: Optional[str] = None
    related_achievement_id: Optional[str] = None
    
    # Metadata
    project_name: Optional[str] = None
    task_name: Optional[str] = None
    priority: Optional[PriorityEnum] = None
    
    # Notification state
    is_read: bool = False
    read_at: Optional[datetime] = None
    channels: List[str] = ["browser"]  # browser, email
    
    # Scheduling (for future notifications)
    scheduled_for: Optional[datetime] = None
    sent_at: Optional[datetime] = None

class BrowserNotificationCreate(BaseModel):
    type: NotificationTypeEnum
    title: str
    message: str
    related_task_id: Optional[str] = None
    related_project_id: Optional[str] = None
    related_area_id: Optional[str] = None
    related_pillar_id: Optional[str] = None
    related_achievement_id: Optional[str] = None
    project_name: Optional[str] = None
    task_name: Optional[str] = None
    priority: Optional[PriorityEnum] = None
    channels: List[str] = ["browser"]
    scheduled_for: Optional[datetime] = None

class BrowserNotificationResponse(BaseModel):
    id: str
    user_id: str
    type: NotificationTypeEnum
    title: str
    message: str
    related_task_id: Optional[str] = None
    related_project_id: Optional[str] = None
    project_name: Optional[str] = None
    task_name: Optional[str] = None
    priority: Optional[PriorityEnum] = None
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime
    sent_at: Optional[datetime] = None

class NotificationPreference(BaseDocument):
    user_id: str
    
    # Channel preferences
    email_notifications: bool = True
    browser_notifications: bool = True
    
    # Notification type preferences
    task_due_notifications: bool = True
    task_overdue_notifications: bool = True
    task_reminder_notifications: bool = True
    project_deadline_notifications: bool = True
    recurring_task_notifications: bool = True
    achievement_notifications: bool = True  # For achievement unlocks
    unblocked_task_notifications: bool = True  # For task dependency notifications
    
    # Timing preferences
    reminder_advance_time: int = 30  # minutes before due time
    overdue_check_interval: int = 60  # minutes between overdue checks
    quiet_hours_start: Optional[str] = "22:00"  # No notifications after this time
    quiet_hours_end: Optional[str] = "08:00"    # Resume notifications after this time
    
    # Email preferences
    daily_digest: bool = False  # Send daily summary email
    weekly_digest: bool = True  # Send weekly summary email

class NotificationPreferenceCreate(BaseModel):
    email_notifications: bool = True
    browser_notifications: bool = True
    task_due_notifications: bool = True
    task_overdue_notifications: bool = True
    task_reminder_notifications: bool = True
    project_deadline_notifications: bool = True
    recurring_task_notifications: bool = True
    achievement_notifications: bool = True
    unblocked_task_notifications: bool = True
    reminder_advance_time: int = 30
    overdue_check_interval: int = 60
    quiet_hours_start: Optional[str] = "22:00"
    quiet_hours_end: Optional[str] = "08:00"
    daily_digest: bool = False
    weekly_digest: bool = True

class NotificationPreferenceUpdate(BaseModel):
    email_notifications: Optional[bool] = None
    browser_notifications: Optional[bool] = None
    task_due_notifications: Optional[bool] = None
    task_overdue_notifications: Optional[bool] = None
    task_reminder_notifications: Optional[bool] = None
    project_deadline_notifications: Optional[bool] = None
    recurring_task_notifications: Optional[bool] = None
    achievement_notifications: Optional[bool] = None
    unblocked_task_notifications: Optional[bool] = None
    reminder_advance_time: Optional[int] = None
    overdue_check_interval: Optional[int] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    daily_digest: Optional[bool] = None
    weekly_digest: Optional[bool] = None

class TaskReminder(BaseDocument):
    user_id: str
    task_id: str
    notification_type: NotificationTypeEnum
    
    # Scheduling
    scheduled_time: datetime
    sent_at: Optional[datetime] = None
    is_sent: bool = False
    
    # Notification details
    title: str
    message: str
    channels: List[NotificationChannelEnum] = [NotificationChannelEnum.browser]
    
    # Metadata
    task_name: Optional[str] = None
    project_name: Optional[str] = None
    priority: Optional[PriorityEnum] = None
    
    # Retry logic
    retry_count: int = 0
    max_retries: int = 3
    next_retry: Optional[datetime] = None

class TaskReminderCreate(BaseModel):
    task_id: str
    notification_type: NotificationTypeEnum
    scheduled_time: datetime
    title: str
    message: str
    channels: List[NotificationChannelEnum] = [NotificationChannelEnum.browser]

class NotificationResponse(BaseModel):
    id: str
    type: NotificationTypeEnum
    title: str
    message: str
    scheduled_time: datetime
    sent_at: Optional[datetime]
    is_sent: bool
    task_name: Optional[str]
    project_name: Optional[str]
    priority: Optional[PriorityEnum]
    created_at: datetime

# File Management Models
class FileTypeEnum(str, Enum):
    document = "document"  # PDF, DOC, DOCX, TXT, RTF
    image = "image"        # PNG, JPG, JPEG, GIF, SVG
    spreadsheet = "spreadsheet"  # XLS, XLSX, CSV
    presentation = "presentation"  # PPT, PPTX
    archive = "archive"    # ZIP, RAR, TAR
    other = "other"

class ResourceCategoryEnum(str, Enum):
    reference = "reference"
    template = "template"
    attachment = "attachment"
    archive = "archive"
    media = "media"
    document = "document"

class Resource(BaseDocument):
    """File/Resource model for contextual attachments with Supabase Storage"""
    user_id: str
    filename: str
    original_filename: str  # Original name when uploaded
    file_type: FileTypeEnum
    category: ResourceCategoryEnum = ResourceCategoryEnum.document  
    mime_type: str
    file_size: int  # Size in bytes
    
    # Supabase Storage fields (replaces base64 file_content)
    storage_bucket: str  # Supabase Storage bucket name
    storage_path: str    # Path in Supabase Storage
    file_url: Optional[str] = None  # Public URL if available
    
    # Legacy field for backward compatibility (deprecated)
    file_content: Optional[str] = None  # Base64 encoded - only for migration
    
    description: str = ""
    tags: List[str] = []
    
    # File metadata
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    last_accessed: Optional[datetime] = None
    access_count: int = 0
    
    # Contextual attachment - direct parent relationship
    parent_id: Optional[str] = None  # ID of parent entity (project, task, etc.)
    parent_type: Optional[str] = None  # Type of parent entity ('project', 'task', etc.)
    
    # Legacy attachment relationships (deprecated but kept for backward compatibility)
    attached_to_tasks: List[str] = []      # Task IDs this file is attached to
    attached_to_projects: List[str] = []   # Project IDs this file is attached to  
    attached_to_areas: List[str] = []      # Area IDs this file is attached to
    attached_to_pillars: List[str] = []    # Pillar IDs this file is attached to
    attached_to_journal_entries: List[str] = []  # Journal entry IDs this file is attached to
    
    # File versioning
    version: int = 1
    parent_resource_id: Optional[str] = None  # For file versions
    is_current_version: bool = True
    
    # Organization
    folder_path: str = "/"  # Virtual folder structure
    is_archived: bool = False
    is_favorite: bool = False

class ResourceCreate(BaseModel):
    filename: str
    original_filename: str
    file_type: FileTypeEnum
    category: ResourceCategoryEnum = ResourceCategoryEnum.document
    mime_type: str
    file_size: int
    
    # Supabase Storage fields
    storage_bucket: Optional[str] = None
    storage_path: Optional[str] = None
    file_url: Optional[str] = None
    
    # Legacy base64 content for backward compatibility
    file_content: Optional[str] = None  # Base64 encoded file content
    
    description: str = ""
    tags: List[str] = []
    folder_path: str = "/"
    
    # Contextual attachment fields
    parent_id: Optional[str] = None  # ID of parent entity
    parent_type: Optional[str] = None  # Type of parent entity ('project', 'task')

class ResourceUpdate(BaseModel):
    filename: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[ResourceCategoryEnum] = None
    folder_path: Optional[str] = None
    is_archived: Optional[bool] = None
    is_favorite: Optional[bool] = None

class ResourceResponse(BaseModel):
    id: str
    user_id: str
    filename: str
    original_filename: str
    file_type: FileTypeEnum
    category: ResourceCategoryEnum
    mime_type: str
    file_size: int
    description: str
    tags: List[str]
    upload_date: datetime
    last_accessed: Optional[datetime]
    access_count: int
    
    # Contextual attachment fields
    parent_id: Optional[str] = None
    parent_type: Optional[str] = None
    
    # Legacy attachment relationships (deprecated)
    attached_to_tasks: List[str]
    attached_to_projects: List[str]
    attached_to_areas: List[str]
    attached_to_pillars: List[str]
    attached_to_journal_entries: List[str]
    
    version: int
    parent_resource_id: Optional[str]
    is_current_version: bool
    folder_path: str
    is_archived: bool
    is_favorite: bool
    created_at: datetime
    updated_at: datetime
    
    # Computed fields
    file_size_mb: float = 0.0
    attachments_count: int = 0

class FileAttachmentRequest(BaseModel):
    """Request model for attaching files to entities"""
    resource_id: str
    entity_type: str  # "task", "project", "area", "pillar", "journal_entry"
    entity_id: str

class EntityAttachmentRequest(BaseModel):
    """Request model for attaching files to entities (without resource_id)"""
    entity_type: str  # "task", "project", "area", "pillar", "journal_entry"
    entity_id: str

# Chunked Upload Models for large files
class ChunkedUploadSession(BaseDocument):
    """Track chunked file upload sessions"""
    user_id: str
    session_id: str
    filename: str
    original_filename: str
    total_size: int
    chunk_size: int
    total_chunks: int
    uploaded_chunks: List[int] = []  # List of uploaded chunk numbers
    file_type: FileTypeEnum
    mime_type: str
    is_complete: bool = False
    expires_at: datetime
    
class ChunkedUploadChunk(BaseModel):
    """Individual chunk data"""
    session_id: str
    chunk_number: int
    chunk_data: str  # Base64 encoded chunk
    chunk_size: int

# Custom Achievement Models for Phase 2
class CustomAchievementTargetTypeEnum(str, Enum):
    complete_project = "complete_project"
    complete_tasks = "complete_tasks" 
    write_journal_entries = "write_journal_entries"
    complete_courses = "complete_courses"
    maintain_streak = "maintain_streak"
    reach_level = "reach_level"
    earn_points = "earn_points"

class CustomAchievement(BaseDocument):
    """User-defined custom achievement"""
    user_id: str
    name: str
    description: str = ""
    icon: str = "🎯"
    
    # Goal configuration
    target_type: CustomAchievementTargetTypeEnum
    target_id: Optional[str] = None  # Specific project_id, course_id, etc.
    target_count: int = 1  # Number to achieve (e.g., 5 tasks, 10 entries)
    
    # Achievement state
    is_active: bool = True
    is_completed: bool = False
    completed_date: Optional[datetime] = None
    current_progress: int = 0  # Current count toward target
    
    # Metadata
    created_date: datetime = Field(default_factory=datetime.utcnow)

class CustomAchievementCreate(BaseModel):
    name: str
    description: str = ""
    icon: str = "🎯"
    target_type: CustomAchievementTargetTypeEnum
    target_id: Optional[str] = None
    target_count: int = 1

class CustomAchievementUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

# ----------------
# Login Streak Models
# ----------------
class LoginEvent(BaseModel):
    user_id: str
    login_date_utc: date
    client_timezone: Optional[str] = None
    created_at: datetime

class LoginStreakStats(BaseModel):
    current_streak: int = 0
    best_streak: int = 0

class MonthLoginRequest(BaseModel):
    year: int
    month: int  # 1-12

class MonthLoginResponse(BaseModel):
    year: int
    month: int
    days: List[int]  # days of month (1-based) that had a login

    icon: Optional[str] = None
    target_count: Optional[int] = None
    is_active: Optional[bool] = None

class CustomAchievementResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: str
    icon: str
    target_type: CustomAchievementTargetTypeEnum
    target_id: Optional[str] = None
    target_count: int
    is_active: bool
    is_completed: bool
    completed_date: Optional[datetime] = None
    current_progress: int
    progress_percentage: float
    created_date: datetime
    
    # Contextual information
    target_name: Optional[str] = None  # Name of target project/course etc.
    estimated_completion: Optional[datetime] = None  # Based on current progress

# Feedback System Models
class FeedbackCategoryEnum(str, Enum):
    suggestion = "suggestion"
    bug_report = "bug_report"
    feature_request = "feature_request"
    question = "question"
    complaint = "complaint"
    compliment = "compliment"

class FeedbackPriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"

class Feedback(BaseDocument):
    """User feedback and support requests"""
    user_id: str
    user_email: str
    user_name: str
    category: FeedbackCategoryEnum
    priority: FeedbackPriorityEnum
    subject: str
    message: str
    
    # Status tracking
    status: str = "open"  # open, in_progress, resolved, closed
    admin_response: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    
    # Email tracking
    email_sent: bool = False
    email_sent_at: Optional[datetime] = None
    email_error: Optional[str] = None

class FeedbackCreate(BaseModel):
    category: FeedbackCategoryEnum
    priority: FeedbackPriorityEnum
    subject: str
    message: str

class FeedbackResponse(BaseModel):
    id: str
    user_id: str
    user_email: str
    user_name: str
    category: FeedbackCategoryEnum
    priority: FeedbackPriorityEnum
    subject: str
    message: str
    status: str
    email_sent: bool
    created_at: datetime
    updated_at: datetime