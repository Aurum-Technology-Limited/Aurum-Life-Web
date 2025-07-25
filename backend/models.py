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
    email: str
    username: str
    password_hash: Optional[str] = None  # Optional for Google OAuth users
    first_name: str
    last_name: str
    google_id: Optional[str] = None  # Google OAuth ID
    profile_picture: Optional[str] = None  # URL to profile picture
    is_active: bool = True
    level: int = 1
    total_points: int = 0
    current_streak: int = 0

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
    date_created: datetime = Field(default_factory=datetime.utcnow)

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

# Task Reminders & Notifications Models
class NotificationTypeEnum(str, Enum):
    task_due = "task_due"
    task_overdue = "task_overdue"
    task_reminder = "task_reminder"
    project_deadline = "project_deadline"
    recurring_task = "recurring_task"

class NotificationChannelEnum(str, Enum):
    browser = "browser"
    email = "email"
    both = "both"

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
    """File/Resource model for document management"""
    user_id: str
    filename: str
    original_filename: str  # Original name when uploaded
    file_type: FileTypeEnum
    category: ResourceCategoryEnum = ResourceCategoryEnum.document  
    mime_type: str
    file_size: int  # Size in bytes
    file_content: str  # Base64 encoded file content for reliable storage/display
    description: str = ""
    tags: List[str] = []
    
    # File metadata
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    last_accessed: Optional[datetime] = None
    access_count: int = 0
    
    # Attachment relationships
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
    file_content: str  # Base64 encoded
    description: str = ""
    tags: List[str] = []
    folder_path: str = "/"

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