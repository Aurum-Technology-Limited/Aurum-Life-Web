"""
GraphQL Schema Definition using Strawberry
Efficient data fetching with type safety
"""

import strawberry
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum
import json

# Enums
@strawberry.enum
class TaskStatus(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"

@strawberry.enum
class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@strawberry.enum
class ProjectStatus(Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    ON_HOLD = "On Hold"

# Types
@strawberry.type
class User:
    id: strawberry.ID
    email: str
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    profile_picture: Optional[str]
    is_active: bool
    created_at: datetime
    
    # Computed fields
    @strawberry.field
    def full_name(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username or self.email

@strawberry.type
class Pillar:
    id: strawberry.ID
    user_id: strawberry.ID
    name: str
    description: str
    icon: str
    color: str
    sort_order: int
    archived: bool
    created_at: datetime
    updated_at: datetime
    
    # Related fields (resolved separately)
    areas: Optional[List['Area']] = None
    time_allocation_percentage: Optional[float] = None
    vision_statement: Optional[str] = None
    alignment_strength: Optional[float] = None

@strawberry.type
class Area:
    id: strawberry.ID
    user_id: strawberry.ID
    pillar_id: Optional[strawberry.ID]
    name: str
    description: str
    icon: str
    color: str
    importance: int
    archived: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime
    
    # Related fields
    pillar: Optional[Pillar] = None
    projects: Optional[List['Project']] = None
    time_allocation_actual: Optional[float] = None
    time_allocation_recommended: Optional[float] = None
    balance_score: Optional[float] = None

@strawberry.type
class Project:
    id: strawberry.ID
    user_id: strawberry.ID
    area_id: strawberry.ID
    name: str
    description: str
    icon: str
    deadline: Optional[datetime]
    status: ProjectStatus
    priority: Priority
    importance: int
    completion_percentage: float
    archived: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime
    
    # Related fields
    area: Optional[Area] = None
    tasks: Optional[List['Task']] = None
    hrm_health_score: Optional[float] = None
    hrm_predicted_completion: Optional[date] = None
    goal_coherence_score: Optional[float] = None

@strawberry.type
class Task:
    id: strawberry.ID
    user_id: strawberry.ID
    project_id: strawberry.ID
    parent_task_id: Optional[strawberry.ID]
    name: str
    description: str
    status: TaskStatus
    priority: Priority
    due_date: Optional[datetime]
    reminder_date: Optional[datetime]
    completed: bool
    completed_at: Optional[datetime]
    estimated_duration: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    # Related fields
    project: Optional[Project] = None
    parent_task: Optional['Task'] = None
    subtasks: Optional[List['Task']] = None
    hrm_priority_score: Optional[float] = None
    hrm_reasoning_summary: Optional[str] = None
    ai_suggested_timeblock: Optional[str] = None

@strawberry.type
class JournalEntry:
    id: strawberry.ID
    user_id: strawberry.ID
    title: str
    content: str
    mood: Optional[str]
    energy_level: Optional[str]
    tags: List[str]
    word_count: int
    created_at: datetime
    updated_at: datetime
    
    # Sentiment analysis fields
    sentiment_score: Optional[float] = None
    sentiment_category: Optional[str] = None
    emotional_keywords: Optional[List[str]] = None
    dominant_emotions: Optional[List[str]] = None

@strawberry.type
class AlignmentScore:
    id: strawberry.ID
    user_id: strawberry.ID
    task_id: strawberry.ID
    points_earned: int
    task_priority: Optional[str]
    project_priority: Optional[str]
    area_importance: Optional[int]
    created_at: datetime
    
    # Related
    task: Optional[Task] = None

@strawberry.type
class DailyReflection:
    id: strawberry.ID
    user_id: strawberry.ID
    reflection_date: date
    reflection_text: str
    completion_score: Optional[int]
    mood: Optional[str]
    biggest_accomplishment: Optional[str]
    challenges_faced: Optional[str]
    tomorrow_focus: Optional[str]
    created_at: datetime

@strawberry.type
class Insight:
    id: strawberry.ID
    user_id: strawberry.ID
    entity_type: str
    entity_id: Optional[strawberry.ID]
    insight_type: str
    title: str
    summary: str
    confidence_score: float
    impact_score: Optional[float]
    is_active: bool
    is_pinned: bool
    created_at: datetime
    
    # Detailed reasoning (optional to reduce payload)
    detailed_reasoning: Optional[Dict[str, Any]] = None

# Aggregate Types
@strawberry.type
class TaskStats:
    total: int
    completed: int
    in_progress: int
    overdue: int
    completion_rate: float

@strawberry.type
class ProjectStats:
    total: int
    completed: int
    in_progress: int
    on_hold: int
    average_completion: float

@strawberry.type
class UserStats:
    task_stats: TaskStats
    project_stats: ProjectStats
    total_journal_entries: int
    total_areas: int
    total_pillars: int
    current_streak: int
    total_points: int

@strawberry.type
class DashboardData:
    user_stats: UserStats
    recent_tasks: List[Task]
    upcoming_deadlines: List[Task]
    recent_insights: List[Insight]
    alignment_trend: List[AlignmentScore]

# Input Types for Mutations
@strawberry.input
class CreateTaskInput:
    project_id: strawberry.ID
    name: str
    description: Optional[str] = ""
    priority: Priority = Priority.MEDIUM
    due_date: Optional[datetime] = None
    estimated_duration: Optional[int] = None

@strawberry.input
class UpdateTaskInput:
    id: strawberry.ID
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[Priority] = None
    due_date: Optional[datetime] = None
    completed: Optional[bool] = None

@strawberry.input
class CreateProjectInput:
    area_id: strawberry.ID
    name: str
    description: Optional[str] = ""
    icon: str = "🚀"
    deadline: Optional[datetime] = None
    priority: Priority = Priority.MEDIUM
    importance: int = 3

@strawberry.input
class UpdateProjectInput:
    id: strawberry.ID
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    priority: Optional[Priority] = None
    deadline: Optional[datetime] = None
    completion_percentage: Optional[float] = None

@strawberry.input
class CreateJournalEntryInput:
    title: str
    content: str
    mood: Optional[str] = None
    energy_level: Optional[str] = None
    tags: List[str] = strawberry.field(default_factory=list)

@strawberry.input
class PaginationInput:
    limit: int = 20
    offset: int = 0
    
@strawberry.input
class TaskFilterInput:
    status: Optional[TaskStatus] = None
    priority: Optional[Priority] = None
    project_id: Optional[strawberry.ID] = None
    completed: Optional[bool] = None
    has_due_date: Optional[bool] = None

@strawberry.input
class ProjectFilterInput:
    status: Optional[ProjectStatus] = None
    priority: Optional[Priority] = None
    area_id: Optional[strawberry.ID] = None
    archived: Optional[bool] = False

# Response Types
@strawberry.type
class TaskConnection:
    tasks: List[Task]
    total_count: int
    has_next_page: bool
    
@strawberry.type
class ProjectConnection:
    projects: List[Project]
    total_count: int
    has_next_page: bool

@strawberry.type
class JournalEntryConnection:
    entries: List[JournalEntry]
    total_count: int
    has_next_page: bool

@strawberry.type
class MutationResponse:
    success: bool
    message: Optional[str]
    
@strawberry.type
class TaskMutationResponse(MutationResponse):
    task: Optional[Task] = None
    
@strawberry.type
class ProjectMutationResponse(MutationResponse):
    project: Optional[Project] = None
    
@strawberry.type
class JournalMutationResponse(MutationResponse):
    entry: Optional[JournalEntry] = None