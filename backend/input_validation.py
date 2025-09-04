"""
Input Validation Middleware and Utilities
Provides comprehensive input validation for API requests
"""

import re
import bleach
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, validator, Field
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
import json

# Common validation patterns
PATTERNS = {
    'uuid': re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.I),
    'email': re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
    'username': re.compile(r'^[a-zA-Z0-9_-]{3,30}$'),
    'safe_text': re.compile(r'^[a-zA-Z0-9\s\-_.,!?\'\"()]+$'),
    'no_script': re.compile(r'<script|javascript:|onerror=|onclick=|onload=', re.I),
}

# Maximum lengths for different field types
MAX_LENGTHS = {
    'name': 255,
    'title': 255,
    'description': 2000,
    'content': 10000,
    'short_text': 100,
    'tag': 50,
}

def sanitize_html(text: str, allowed_tags: List[str] = None) -> str:
    """
    Sanitize HTML content to prevent XSS attacks
    """
    if allowed_tags is None:
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li']
    
    allowed_attributes = {
        'a': ['href', 'title'],
    }
    
    return bleach.clean(
        text,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )

def validate_uuid(value: str) -> str:
    """Validate UUID format"""
    if not PATTERNS['uuid'].match(value):
        raise ValueError(f"Invalid UUID format: {value}")
    return value.lower()

def validate_email(email: str) -> str:
    """Validate email format"""
    if not PATTERNS['email'].match(email):
        raise ValueError(f"Invalid email format: {email}")
    return email.lower()

def validate_username(username: str) -> str:
    """Validate username format"""
    if not PATTERNS['username'].match(username):
        raise ValueError(f"Invalid username format. Use 3-30 characters, alphanumeric, underscore, or hyphen only.")
    return username

def validate_text_length(text: str, field_name: str, max_length: Optional[int] = None) -> str:
    """Validate text length"""
    if max_length is None:
        max_length = MAX_LENGTHS.get(field_name, 1000)
    
    if len(text) > max_length:
        raise ValueError(f"{field_name} exceeds maximum length of {max_length} characters")
    
    return text

def validate_no_script_injection(text: str) -> str:
    """Check for potential script injection"""
    if PATTERNS['no_script'].search(text):
        raise ValueError("Potentially malicious content detected")
    return text

def validate_array_length(array: List[Any], field_name: str, max_length: int = 100) -> List[Any]:
    """Validate array length"""
    if len(array) > max_length:
        raise ValueError(f"{field_name} exceeds maximum array length of {max_length}")
    return array

def validate_safe_filename(filename: str) -> str:
    """Validate filename for safety"""
    # Remove path components
    filename = filename.replace('..', '').replace('/', '').replace('\\', '')
    
    # Check for common dangerous extensions
    dangerous_extensions = ['.exe', '.bat', '.cmd', '.sh', '.ps1', '.vbs', '.js']
    if any(filename.lower().endswith(ext) for ext in dangerous_extensions):
        raise ValueError("Dangerous file type not allowed")
    
    # Limit filename length
    if len(filename) > 255:
        raise ValueError("Filename too long")
    
    return filename

# Pydantic models with built-in validation
class ValidatedTaskCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    project_id: str
    priority: str = Field("medium", regex="^(low|medium|high)$")
    status: str = Field("todo", regex="^(todo|in_progress|review|completed)$")
    
    @validator('name', 'description')
    def validate_no_scripts(cls, v):
        if v:
            return validate_no_script_injection(v)
        return v
    
    @validator('project_id')
    def validate_project_uuid(cls, v):
        return validate_uuid(v)

class ValidatedProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    area_id: str
    priority: str = Field("medium", regex="^(low|medium|high)$")
    
    @validator('name', 'description')
    def sanitize_text(cls, v):
        if v:
            return sanitize_html(v, allowed_tags=[])
        return v
    
    @validator('area_id')
    def validate_area_uuid(cls, v):
        return validate_uuid(v)

class ValidatedJournalEntry(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1, max_length=10000)
    mood: Optional[str] = Field(None, regex="^(optimistic|inspired|reflective|challenging|anxious|grateful|excited|frustrated|peaceful|motivated)$")
    tags: Optional[List[str]] = Field(default_factory=list, max_items=20)
    
    @validator('title')
    def validate_title(cls, v):
        return validate_no_script_injection(v)
    
    @validator('content')
    def sanitize_content(cls, v):
        # Allow some formatting tags for journal entries
        return sanitize_html(v, allowed_tags=['p', 'br', 'strong', 'em', 'u', 'blockquote'])
    
    @validator('tags')
    def validate_tags(cls, v):
        if v:
            validated_tags = []
            for tag in v:
                if len(tag) > MAX_LENGTHS['tag']:
                    raise ValueError(f"Tag '{tag}' exceeds maximum length")
                validated_tags.append(validate_no_script_injection(tag))
            return validated_tags
        return v

class InputValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate and sanitize all incoming request data
    """
    
    # Endpoints that require strict validation
    VALIDATED_ENDPOINTS = {
        '/api/tasks': ValidatedTaskCreate,
        '/api/projects': ValidatedProjectCreate,
        '/api/journal': ValidatedJournalEntry,
    }
    
    async def dispatch(self, request: Request, call_next):
        # Only validate POST, PUT, PATCH requests
        if request.method in ["POST", "PUT", "PATCH"]:
            # Check if this endpoint needs validation
            path = request.url.path
            
            # Get request body
            body = await request.body()
            
            if body:
                try:
                    # Parse JSON
                    data = json.loads(body)
                    
                    # General validation for all requests
                    self.validate_request_size(body)
                    self.validate_nested_depth(data)
                    
                    # Specific validation for certain endpoints
                    if path in self.VALIDATED_ENDPOINTS:
                        model_class = self.VALIDATED_ENDPOINTS[path]
                        # This will raise validation errors if data is invalid
                        validated_data = model_class(**data)
                        
                        # Replace request body with validated data
                        request._body = validated_data.json().encode()
                    
                except json.JSONDecodeError:
                    raise HTTPException(status_code=400, detail="Invalid JSON format")
                except ValueError as e:
                    raise HTTPException(status_code=422, detail=str(e))
                except Exception as e:
                    raise HTTPException(status_code=422, detail=f"Validation error: {str(e)}")
        
        response = await call_next(request)
        return response
    
    def validate_request_size(self, body: bytes, max_size: int = 10 * 1024 * 1024):  # 10MB
        """Validate request body size"""
        if len(body) > max_size:
            raise ValueError(f"Request body too large. Maximum size is {max_size} bytes")
    
    def validate_nested_depth(self, data: Any, max_depth: int = 10, current_depth: int = 0):
        """Prevent deeply nested objects that could cause DoS"""
        if current_depth > max_depth:
            raise ValueError(f"Data structure too deeply nested. Maximum depth is {max_depth}")
        
        if isinstance(data, dict):
            for value in data.values():
                self.validate_nested_depth(value, max_depth, current_depth + 1)
        elif isinstance(data, list):
            for item in data:
                self.validate_nested_depth(item, max_depth, current_depth + 1)

# Utility functions for manual validation
def validate_and_sanitize_input(data: Dict[str, Any], field_rules: Dict[str, Dict]) -> Dict[str, Any]:
    """
    Validate and sanitize input data based on field rules
    
    Example:
    field_rules = {
        'name': {'type': 'text', 'max_length': 255, 'required': True},
        'email': {'type': 'email', 'required': True},
        'tags': {'type': 'array', 'max_items': 10},
    }
    """
    validated_data = {}
    
    for field, rules in field_rules.items():
        value = data.get(field)
        
        # Check required fields
        if rules.get('required') and value is None:
            raise ValueError(f"{field} is required")
        
        if value is not None:
            # Type-specific validation
            field_type = rules.get('type', 'text')
            
            if field_type == 'text':
                value = str(value)
                if 'max_length' in rules:
                    value = validate_text_length(value, field, rules['max_length'])
                value = validate_no_script_injection(value)
                
            elif field_type == 'email':
                value = validate_email(value)
                
            elif field_type == 'uuid':
                value = validate_uuid(value)
                
            elif field_type == 'array':
                if not isinstance(value, list):
                    raise ValueError(f"{field} must be an array")
                if 'max_items' in rules:
                    value = validate_array_length(value, field, rules['max_items'])
                    
            elif field_type == 'html':
                allowed_tags = rules.get('allowed_tags', [])
                value = sanitize_html(value, allowed_tags)
            
            validated_data[field] = value
    
    return validated_data