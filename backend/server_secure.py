"""
Secure FastAPI server configuration for Aurum Life MVP v1.2
Authentication: Supabase Auth only (no legacy JWT fallback)
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from typing import Optional
import logging

# Import secure dependencies
from supabase_auth import verify_supabase_token, get_current_user
from mvp_performance_monitor import performance_middleware, perf_router
from mvp_today_service import today_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()

# Create FastAPI app with security defaults
app = FastAPI(
    title="Aurum Life API",
    version="1.2.0",
    docs_url=None,  # Disable in production
    redoc_url=None  # Disable in production
)

# CORS configuration - restrictive by default
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
    max_age=86400,  # 24 hours
)

# Add performance monitoring
app.middleware("http")(performance_middleware)

# Secure authentication dependency
async def get_current_active_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Verify user authentication using ONLY Supabase Auth.
    No fallback to legacy JWT system.
    """
    try:
        # Verify token with Supabase
        user = await verify_supabase_token(credentials.credentials)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Additional security check - ensure user is active
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated"
            )
            
        return user
        
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Health check endpoint (no auth required)
@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.2.0",
        "service": "aurum-life-api"
    }

# Include routers with authentication
app.include_router(
    today_router,
    dependencies=[Depends(get_current_active_user)]
)

app.include_router(
    perf_router,
    prefix="/api/admin",
    dependencies=[Depends(get_current_active_user)]
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return {
        "detail": "An internal error occurred",
        "status_code": 500
    }