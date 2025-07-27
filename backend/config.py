"""
Secure Configuration Management for Aurum Life MVP v1.2
Uses Pydantic for validation and type safety of all environment variables
"""

from pydantic import BaseSettings, validator, Field
from typing import Optional, List
import os
from functools import lru_cache

class Settings(BaseSettings):
    """
    Application settings with validation and security checks
    All sensitive values MUST come from environment variables
    """
    
    # Application
    app_name: str = "Aurum Life API"
    app_version: str = "1.2.0"
    environment: str = Field(..., env="ENVIRONMENT")  # Required: development, staging, production
    debug: bool = Field(False, env="DEBUG")
    
    # Security
    secret_key: str = Field(..., env="SECRET_KEY", min_length=32)
    allowed_origins: List[str] = Field([], env="ALLOWED_ORIGINS")
    
    # Supabase Configuration
    supabase_url: str = Field(..., env="SUPABASE_URL")
    supabase_anon_key: str = Field(..., env="SUPABASE_ANON_KEY")
    supabase_service_key: Optional[str] = Field(None, env="SUPABASE_SERVICE_KEY")
    supabase_jwt_secret: str = Field(..., env="SUPABASE_JWT_SECRET")
    
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    database_pool_size: int = Field(20, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(40, env="DATABASE_MAX_OVERFLOW")
    
    # Redis Configuration
    redis_url: str = Field("redis://localhost:6379", env="REDIS_URL")
    redis_password: Optional[str] = Field(None, env="REDIS_PASSWORD")
    
    # Celery Configuration
    celery_broker_url: str = Field(..., env="CELERY_BROKER_URL")
    celery_result_backend: str = Field(..., env="CELERY_RESULT_BACKEND")
    celery_task_timeout: int = Field(300, env="CELERY_TASK_TIMEOUT")  # 5 minutes
    
    # API Rate Limiting
    rate_limit_per_minute: int = Field(60, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_per_hour: int = Field(1000, env="RATE_LIMIT_PER_HOUR")
    
    # Performance Settings
    api_timeout_seconds: int = Field(30, env="API_TIMEOUT_SECONDS")
    max_request_size: int = Field(10485760, env="MAX_REQUEST_SIZE")  # 10MB
    
    # Logging
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_format: str = Field("json", env="LOG_FORMAT")  # json or text
    
    @validator("environment")
    def validate_environment(cls, v):
        """Ensure environment is valid"""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of: {allowed}")
        return v
    
    @validator("debug")
    def validate_debug(cls, v, values):
        """Ensure debug is disabled in production"""
        if values.get("environment") == "production" and v:
            raise ValueError("Debug mode cannot be enabled in production")
        return v
    
    @validator("supabase_url")
    def validate_supabase_url(cls, v):
        """Validate Supabase URL format"""
        if not v.startswith("https://") or not v.endswith(".supabase.co"):
            raise ValueError("Invalid Supabase URL format")
        return v
    
    @validator("database_url")
    def validate_database_url(cls, v):
        """Validate PostgreSQL connection string"""
        if not v.startswith(("postgresql://", "postgres://")):
            raise ValueError("Invalid PostgreSQL URL format")
        return v
    
    @validator("allowed_origins")
    def parse_allowed_origins(cls, v):
        """Parse comma-separated origins"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    @validator("secret_key")
    def validate_secret_key(cls, v, values):
        """Ensure secret key is strong in production"""
        if values.get("environment") == "production":
            if len(v) < 64:
                raise ValueError("Production secret key must be at least 64 characters")
            # Check for common weak patterns
            if v.lower() in ["secret", "password", "changeme"] or v.isdigit():
                raise ValueError("Secret key is too weak for production")
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == "development"
    
    @property
    def redis_url_with_password(self) -> str:
        """Get Redis URL with password if set"""
        if self.redis_password:
            # Parse and inject password
            from urllib.parse import urlparse, urlunparse
            parsed = urlparse(self.redis_url)
            netloc = f":{self.redis_password}@{parsed.hostname}:{parsed.port}"
            return urlunparse(parsed._replace(netloc=netloc))
        return self.redis_url
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        # Prevent secrets from being logged
        fields = {
            "secret_key": {"exclude": True},
            "supabase_service_key": {"exclude": True},
            "supabase_jwt_secret": {"exclude": True},
            "redis_password": {"exclude": True},
            "database_url": {"exclude": True},
        }

@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    Uses LRU cache to ensure settings are only loaded once
    """
    return Settings()

# Global settings instance
settings = get_settings()

# Validate critical settings on import
if settings.is_production:
    # Additional production checks
    assert settings.supabase_service_key, "Service key required in production"
    assert len(settings.allowed_origins) > 0, "Allowed origins must be set in production"
    assert not settings.debug, "Debug must be disabled in production"