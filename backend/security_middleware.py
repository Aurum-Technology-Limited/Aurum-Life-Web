"""
Security Middleware for Aurum Life API
Implements foundational security hardening measures including:
- HTTP Security Headers (CSP, HSTS, X-Frame-Options, etc.)
- CSRF Protection (Double Submit Cookie pattern)
- Input sanitization utilities
- IDOR (Insecure Direct Object Reference) protection utilities
"""

from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Dict, Any
import bleach
import logging
import secrets
import re
from supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add critical HTTP security headers to all responses
    """
    
    def __init__(self, app, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        
        # Define security headers with hardened CSP
        self.security_headers = {
            # Hardened Content Security Policy - More restrictive
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' https://accounts.google.com https://apis.google.com; "
                "style-src 'self' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https://accounts.google.com https://oauth2.googleapis.com https://www.googleapis.com https://7b39a747-36d6-44f7-9408-a498365475ba.preview.emergentagent.com; "
                "frame-src 'self' https://accounts.google.com; "
                "object-src 'none'; "
                "base-uri 'self'; "
                "form-action 'self'; "
                "frame-ancestors 'self'"
            ),
            
            # HTTP Strict Transport Security - Enforce HTTPS
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            
            # Prevent MIME type sniffing
            "X-Content-Type-Options": "nosniff",
            
            # Prevent clickjacking attacks
            "X-Frame-Options": "SAMEORIGIN",
            
            # Enable XSS protection in browsers
            "X-XSS-Protection": "1; mode=block",
            
            # Control referrer information
            "Referrer-Policy": "strict-origin-when-cross-origin",
            
            # Control browser features and APIs
            "Permissions-Policy": (
                "camera=(), "
                "microphone=(), "
                "geolocation=(), "
                "payment=(), "
                "usb=(), "
                "magnetometer=(), "
                "gyroscope=(), "
                "accelerometer=()"
            ),
            
            # Remove server information
            "Server": "Aurum-Life-API"
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and add security headers to response
        """
        # Process the request
        response = await call_next(request)
        
        # Add security headers to all responses
        for header_name, header_value in self.security_headers.items():
            response.headers[header_name] = header_value
        
        return response


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """
    CSRF Protection using Double Submit Cookie pattern
    """
    
    def __init__(self, app, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        # State-changing methods that require CSRF protection
        self.protected_methods = {"POST", "PUT", "DELETE", "PATCH"}
        # Endpoints that don't need CSRF protection (like login)
        self.exempt_paths = {
            "/api/auth/login",
            "/api/auth/register", 
            "/api/auth/refresh",
            "/"  # Root endpoint
        }
    
    def generate_csrf_token(self) -> str:
        """Generate a secure CSRF token"""
        return secrets.token_urlsafe(32)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and validate CSRF tokens for state-changing operations
        """
        request_path = request.url.path
        request_method = request.method
        
        # Skip CSRF protection for non-protected methods or exempt paths
        if request_method not in self.protected_methods or request_path in self.exempt_paths:
            response = await call_next(request)
            
            # For login endpoint, set CSRF token in cookie
            if request_path == "/api/auth/login" and request_method == "POST":
                csrf_token = self.generate_csrf_token()
                response.set_cookie(
                    key="csrf_token",
                    value=csrf_token,
                    httponly=False,  # JavaScript needs to read this
                    secure=True,     # HTTPS only in production
                    samesite="strict"
                )
                logger.info("CSRF token generated and set in cookie")
            
            return response
        
        # Validate CSRF token for protected requests
        csrf_cookie = request.cookies.get("csrf_token")
        csrf_header = request.headers.get("X-CSRF-Token")
        
        if not csrf_cookie or not csrf_header:
            logger.warning(f"CSRF protection: Missing token - Cookie: {bool(csrf_cookie)}, Header: {bool(csrf_header)}")
            raise HTTPException(
                status_code=403,
                detail="CSRF token missing. This request requires CSRF protection."
            )
        
        if csrf_cookie != csrf_header:
            logger.warning("CSRF protection: Token mismatch")
            raise HTTPException(
                status_code=403,
                detail="CSRF token mismatch. Invalid request."
            )
        
        logger.debug("CSRF protection: Token validated successfully")
        return await call_next(request)


class InputSanitizer:
    """
    Utility class for sanitizing user input to prevent XSS attacks
    """
    
    # Define allowed HTML tags and attributes for specific use cases
    ALLOWED_TAGS = []  # No HTML tags allowed by default
    ALLOWED_ATTRIBUTES = {}
    ALLOWED_PROTOCOLS = []
    
    # For rich text content (if needed in future)
    RICH_TEXT_TAGS = [
        'p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote'
    ]
    RICH_TEXT_ATTRIBUTES = {
        '*': ['class'],
    }
    
    @staticmethod
    def sanitize_string(text: str, allow_html: bool = False) -> str:
        """
        Sanitize user input string to prevent XSS attacks
        
        Args:
            text: The input string to sanitize
            allow_html: Whether to allow basic HTML tags (for rich text)
            
        Returns:
            Sanitized string safe for storage and display
        """
        if not isinstance(text, str):
            return str(text) if text is not None else ""
        
        if not text.strip():
            return text
        
        try:
            if allow_html:
                # For rich text content, allow basic formatting tags
                sanitized = bleach.clean(
                    text,
                    tags=InputSanitizer.RICH_TEXT_TAGS,
                    attributes=InputSanitizer.RICH_TEXT_ATTRIBUTES,
                    protocols=InputSanitizer.ALLOWED_PROTOCOLS,
                    strip=True
                )
            else:
                # For regular text, strip all HTML
                sanitized = bleach.clean(
                    text,
                    tags=InputSanitizer.ALLOWED_TAGS,
                    attributes=InputSanitizer.ALLOWED_ATTRIBUTES,
                    protocols=InputSanitizer.ALLOWED_PROTOCOLS,
                    strip=True
                )
            
            # Additional cleaning - remove potentially dangerous characters
            sanitized = sanitized.replace('\x00', '')  # Remove null bytes
            
            logger.debug(f"Sanitized text: '{text[:50]}...' -> '{sanitized[:50]}...'")
            return sanitized.strip()
            
        except Exception as e:
            logger.error(f"Error sanitizing text: {str(e)}")
            # If sanitization fails, return a safe empty string
            return ""
    
    @staticmethod
    def sanitize_dict(data: Dict[str, Any], allow_html_fields: set = None) -> Dict[str, Any]:
        """
        Recursively sanitize all string values in a dictionary
        
        Args:
            data: Dictionary containing data to sanitize
            allow_html_fields: Set of field names that can contain HTML
            
        Returns:
            Dictionary with sanitized string values
        """
        if not isinstance(data, dict):
            return data
        
        if allow_html_fields is None:
            allow_html_fields = set()
        
        sanitized_data = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                allow_html = key in allow_html_fields
                sanitized_data[key] = InputSanitizer.sanitize_string(value, allow_html=allow_html)
            elif isinstance(value, dict):
                sanitized_data[key] = InputSanitizer.sanitize_dict(value, allow_html_fields)
            elif isinstance(value, list):
                sanitized_data[key] = [
                    InputSanitizer.sanitize_string(item, allow_html=(key in allow_html_fields))
                    if isinstance(item, str)
                    else item
                    for item in value
                ]
            else:
                sanitized_data[key] = value
        
        return sanitized_data


# Utility function to sanitize common user input models
def sanitize_user_input(data: Dict[str, Any], model_type: str = "default") -> Dict[str, Any]:
    """
    Sanitize user input based on the model type
    
    Args:
        data: The data dictionary to sanitize
        model_type: Type of model to determine which fields can contain HTML
        
    Returns:
        Sanitized data dictionary
    """
    # Define which fields can contain basic HTML for different models
    html_allowed_fields = {
        "feedback": {"message"},  # Feedback messages might contain basic formatting
        "journal": {"content", "template_responses"},  # Journal entries might contain formatting
        "default": set()  # No HTML allowed by default
    }
    
    allow_html_fields = html_allowed_fields.get(model_type, set())
    
    return InputSanitizer.sanitize_dict(data, allow_html_fields)


# IDOR Protection Utilities
class IDORProtection:
    """
    Utility class for protecting against Insecure Direct Object Reference attacks
    """
    
    @staticmethod
    async def verify_resource_ownership(
        user_id: str, 
        resource_type: str, 
        resource_id: str, 
        supabase_client=None
    ) -> bool:
        """
        Verify that a user owns a specific resource
        
        Args:
            user_id: The authenticated user's ID
            resource_type: Type of resource (projects, tasks, areas, pillars, etc.)
            resource_id: The ID of the resource to check
            supabase_client: Supabase client instance
            
        Returns:
            True if user owns the resource, False otherwise
        """
        if not supabase_client:
            supabase_client = get_supabase_client()
        
        try:
            # Map resource types to table names
            table_mapping = {
                'project': 'projects',
                'projects': 'projects',
                'task': 'tasks', 
                'tasks': 'tasks',
                'area': 'areas',
                'areas': 'areas',
                'pillar': 'pillars',
                'pillars': 'pillars',
                'journal': 'journal_entries',
                'journal_entry': 'journal_entries',
                'project_template': 'project_templates',
                'journal_template': 'journal_templates'
            }
            
            table_name = table_mapping.get(resource_type.lower())
            if not table_name:
                logger.error(f"Unknown resource type for IDOR check: {resource_type}")
                return False
            
            # Query the resource to check ownership
            response = supabase_client.table(table_name)\
                .select('id')\
                .eq('id', resource_id)\
                .eq('user_id', user_id)\
                .limit(1)\
                .execute()
            
            exists = len(response.data) > 0
            
            if not exists:
                logger.warning(f"IDOR attempt detected: User {user_id} tried to access {resource_type} {resource_id} without ownership")
            else:
                logger.debug(f"IDOR check passed: User {user_id} owns {resource_type} {resource_id}")
                
            return exists
            
        except Exception as e:
            logger.error(f"Error in IDOR ownership check: {str(e)}")
            return False
    
    @staticmethod
    async def verify_ownership_or_404(
        user_id: str,
        resource_type: str, 
        resource_id: str,
        supabase_client=None
    ):
        """
        Verify resource ownership or raise 404 exception
        
        This follows the security requirement to return 404 (not 403) 
        to prevent resource enumeration attacks
        
        Args:
            user_id: The authenticated user's ID
            resource_type: Type of resource 
            resource_id: The ID of the resource to check
            supabase_client: Supabase client instance
            
        Raises:
            HTTPException: 404 if user doesn't own the resource
        """
        owns_resource = await IDORProtection.verify_resource_ownership(
            user_id, resource_type, resource_id, supabase_client
        )
        
        if not owns_resource:
            # Return 404 to prevent resource enumeration (security requirement)
            raise HTTPException(
                status_code=404,
                detail="Resource not found"
            )