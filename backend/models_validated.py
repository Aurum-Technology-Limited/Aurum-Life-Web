"""
Validated Pydantic Models for Aurum Life MVP v1.2
Implements strict input validation and sanitization for all API endpoints
"""

from pydantic import BaseModel, Field, validator, constr, conint
from typing import Optional, List
from datetime import datetime
from enum import Enum
import re
from uuid import UUID

# Constants for validation
MAX_NAME_LENGTH = 100
MAX_DESCRIPTION_LENGTH = 500
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128

# Custom types
SafeString = constr(strip_whitespace=True, max_length=MAX_NAME_LENGTH)
SafeDescription = constr(strip_whitespace=True, max_length=MAX_DESCRIPTION_LENGTH)

# Enums
class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class TaskStatusEnum(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"

class ProjectStatusEnum(str, Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"
    on_hold = "on_hold"

# Base validators
class BaseValidator:
    """Common validators for reuse across models"""
    
    @staticmethod
    def sanitize_html(v: str) -> str:
        """Remove any HTML tags from input"""
        if not v:
            return v
        # Basic HTML tag removal
        clean = re.sub('<.*?>', '', v)
        # Remove multiple spaces
        clean = re.sub(r'\s+', ' ', clean)
        return clean.strip()
    
    @staticmethod
    def validate_no_sql_injection(v: str) -> str:
        """Check for common SQL injection patterns"""
        if not v:
            return v
        
        sql_keywords = [
            'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 
            'UNION', 'OR 1=1', 'AND 1=1', '--', '/*', '*/',
            'EXEC', 'EXECUTE', 'SCRIPT'
        ]
        
        upper_v = v.upper()
        for keyword in sql_keywords:
            if keyword in upper_v:
                raise ValueError(f"Potentially malicious input detected")
        
        return v
    
    @staticmethod
    def validate_color(v: str) -> str:
        """Validate hex color format"""
        if not v:
            return "#000000"
        
        if not re.match(r'^#[0-9A-Fa-f]{6}$', v):
            raise ValueError("Invalid color format. Use hex format: #RRGGBB")
        
        return v.upper()

# User models with validation
class UserCreate(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=MIN_PASSWORD_LENGTH, max_length=MAX_PASSWORD_LENGTH)
    first_name: SafeString = Field(..., min_length=1)
    last_name: SafeString = Field(..., min_length=1)
    
    @validator('email')
    def validate_email(cls, v):
        """Validate email format"""
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, v.lower()):
            raise ValueError('Invalid email format')
        return v.lower()
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < MIN_PASSWORD_LENGTH:
            raise ValueError(f'Password must be at least {MIN_PASSWORD_LENGTH} characters')
        
        # Check complexity
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v)
        
        if not all([has_upper, has_lower, has_digit, has_special]):
            raise ValueError(
                'Password must contain uppercase, lowercase, number, and special character'
            )
        
        return v
    
    @validator('first_name', 'last_name')
    def sanitize_name(cls, v):
        """Sanitize name fields"""
        return BaseValidator.sanitize_html(v)

# Pillar models with validation
class PillarCreate(BaseModel):
    name: SafeString = Field(..., min_length=1)
    description: SafeDescription = Field(default="")
    icon: str = Field(default="🎯", max_length=10)
    color: str = Field(default="#000000")
    time_allocation_percentage: Optional[conint(ge=0, le=100)] = None
    
    @validator('name', 'description')
    def sanitize_text(cls, v):
        """Sanitize text fields"""
        return BaseValidator.sanitize_html(BaseValidator.validate_no_sql_injection(v))
    
    @validator('color')
    def validate_color(cls, v):
        """Validate color format"""
        return BaseValidator.validate_color(v)
    
    @validator('icon')
    def validate_icon(cls, v):
        """Validate icon (emoji or simple string)"""
        if len(v) > 10:
            raise ValueError("Icon too long")
        return v

class PillarUpdate(BaseModel):
    name: Optional[SafeString] = None
    description: Optional[SafeDescription] = None
    icon: Optional[str] = Field(None, max_length=10)
    color: Optional[str] = None
    time_allocation_percentage: Optional[conint(ge=0, le=100)] = None
    archived: Optional[bool] = None
    
    _sanitize_text = validator('name', 'description', allow_reuse=True)(
        lambda v: BaseValidator.sanitize_html(v) if v else None
    )
    _validate_color = validator('color', allow_reuse=True)(
        lambda v: BaseValidator.validate_color(v) if v else None
    )

# Area models with validation  
class AreaCreate(BaseModel):
    pillar_id: str
    name: SafeString = Field(..., min_length=1)
    description: SafeDescription = Field(default="")
    icon: str = Field(default="🎯", max_length=10)
    color: str = Field(default="#000000")
    
    @validator('pillar_id')
    def validate_uuid(cls, v):
        """Validate UUID format"""
        try:
            UUID(v)
        except ValueError:
            raise ValueError("Invalid pillar ID format")
        return v
    
    _sanitize_text = validator('name', 'description', allow_reuse=True)(
        lambda v: BaseValidator.sanitize_html(BaseValidator.validate_no_sql_injection(v))
    )
    _validate_color = validator('color', allow_reuse=True)(
        lambda v: BaseValidator.validate_color(v)
    )

# Project models with validation
class ProjectCreate(BaseModel):
    area_id: str
    name: SafeString = Field(..., min_length=1)
    description: SafeDescription = Field(default="")
    icon: str = Field(default="🚀", max_length=10)
    deadline: Optional[datetime] = None
    status: ProjectStatusEnum = ProjectStatusEnum.not_started
    priority: PriorityEnum = PriorityEnum.medium
    
    @validator('area_id')
    def validate_uuid(cls, v):
        """Validate UUID format"""
        try:
            UUID(v)
        except ValueError:
            raise ValueError("Invalid area ID format")
        return v
    
    @validator('deadline')
    def validate_deadline(cls, v):
        """Ensure deadline is in the future"""
        if v and v < datetime.utcnow():
            raise ValueError("Deadline cannot be in the past")
        return v
    
    _sanitize_text = validator('name', 'description', allow_reuse=True)(
        lambda v: BaseValidator.sanitize_html(BaseValidator.validate_no_sql_injection(v))
    )

# Task models with validation
class TaskCreate(BaseModel):
    project_id: str
    name: SafeString = Field(..., min_length=1)
    description: SafeDescription = Field(default="")
    priority: PriorityEnum = PriorityEnum.medium
    due_date: Optional[datetime] = None
    due_time: Optional[str] = Field(None, regex=r'^([01]\d|2[0-3]):([0-5]\d)$')
    estimated_duration: Optional[conint(ge=1, le=480)] = None  # 1-480 minutes (8 hours max)
    
    @validator('project_id')
    def validate_uuid(cls, v):
        """Validate UUID format"""
        try:
            UUID(v)
        except ValueError:
            raise ValueError("Invalid project ID format")
        return v
    
    @validator('due_date')
    def validate_due_date(cls, v):
        """Validate due date is reasonable"""
        if v:
            # Can be in the past (overdue tasks) but not too far in future
            max_future = datetime.utcnow().replace(year=datetime.utcnow().year + 5)
            if v > max_future:
                raise ValueError("Due date too far in the future")
        return v
    
    _sanitize_text = validator('name', 'description', allow_reuse=True)(
        lambda v: BaseValidator.sanitize_html(BaseValidator.validate_no_sql_injection(v))
    )

class TaskUpdate(BaseModel):
    name: Optional[SafeString] = None
    description: Optional[SafeDescription] = None
    priority: Optional[PriorityEnum] = None
    status: Optional[TaskStatusEnum] = None
    due_date: Optional[datetime] = None
    due_time: Optional[str] = Field(None, regex=r'^([01]\d|2[0-3]):([0-5]\d)$')
    completed: Optional[bool] = None
    estimated_duration: Optional[conint(ge=1, le=480)] = None
    
    _sanitize_text = validator('name', 'description', allow_reuse=True)(
        lambda v: BaseValidator.sanitize_html(v) if v else None
    )

# Request validation models
class PaginationParams(BaseModel):
    """Common pagination parameters"""
    skip: conint(ge=0) = Field(0, description="Number of items to skip")
    limit: conint(ge=1, le=100) = Field(20, description="Number of items to return")
    
class SortParams(BaseModel):
    """Common sort parameters"""
    sort_by: str = Field("created_at", regex=r'^[a-zA-Z_]+$')
    sort_order: str = Field("desc", regex=r'^(asc|desc)$')

# Response models with validation
class APIResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PillarResponse(BaseModel):
    """Pillar response with computed fields"""
    id: str
    user_id: str
    name: str
    description: str
    icon: str
    color: str
    archived: bool
    time_allocation_percentage: Optional[float]
    created_at: datetime
    updated_at: datetime
    
    # Computed fields
    area_count: int = 0
    project_count: int = 0
    task_count: int = 0
    completed_task_count: int = 0
    progress_percentage: float = 0.0
    
    class Config:
        orm_mode = True