from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from enum import Enum

# Base model for common fields
class BaseDocument(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# User models
class User(BaseDocument):
    username: str
    email: str
    level: int = 1
    total_points: int = 0
    current_streak: int = 0
    profile_data: Dict[str, Any] = {}

class UserCreate(BaseModel):
    username: str
    email: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    level: Optional[int] = None
    total_points: Optional[int] = None
    current_streak: Optional[int] = None
    profile_data: Optional[Dict[str, Any]] = None

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

class Task(BaseDocument):
    user_id: str
    title: str
    description: str = ""
    priority: PriorityEnum = PriorityEnum.medium
    due_date: Optional[datetime] = None
    category: str = "personal"
    completed: bool = False
    completed_at: Optional[datetime] = None

class TaskCreate(BaseModel):
    title: str
    description: str = ""
    priority: PriorityEnum = PriorityEnum.medium
    due_date: Optional[datetime] = None
    category: str = "personal"

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[PriorityEnum] = None
    due_date: Optional[datetime] = None
    category: Optional[str] = None
    completed: Optional[bool] = None

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
    courses_enrolled: int = 0
    courses_completed: int = 0
    badges_earned: int = 0
    meditation_sessions: int = 0
    meditation_minutes: int = 0
    last_updated: datetime = Field(default_factory=datetime.utcnow)

# Response models for API
class HabitResponse(Habit):
    progress_percentage: Optional[float] = None

class TaskResponse(Task):
    is_overdue: Optional[bool] = None

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