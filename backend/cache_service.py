"""
Advanced Caching Service with Redis
Provides multi-level caching for API responses and database queries
"""

import json
import logging
import hashlib
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from functools import wraps
import asyncio

# Redis imports with fallback
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)

class CacheService:
    """
    Advanced caching service with multiple storage backends
    Supports both Redis and in-memory caching with intelligent fallback
    """
    
    def __init__(self):
        self.redis_client = None
        self.memory_cache: Dict[str, Dict] = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
        
        # Initialize Redis connection
        if REDIS_AVAILABLE:
            self._initialize_redis()
        else:
            logger.warning("Redis not available, using in-memory cache only")
    
    def _initialize_redis(self):
        """Initialize Redis connection with error handling"""
        try:
            # Use Redis if available (production), fallback to memory cache
            redis_url = "redis://localhost:6379/0"  # Default Redis URL
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            logger.info("✅ Redis cache initialized successfully")
        except Exception as e:
            logger.warning(f"⚠️ Redis initialization failed: {e}, using memory cache")
            self.redis_client = None
    
    def _generate_cache_key(self, prefix: str, user_id: str = None, **kwargs) -> str:
        """Generate consistent cache keys"""
        key_parts = [prefix]
        
        if user_id:
            key_parts.append(f"user:{user_id}")
        
        # Sort kwargs for consistent key generation
        for key, value in sorted(kwargs.items()):
            if value is not None:
                key_parts.append(f"{key}:{value}")
        
        cache_key = ":".join(key_parts)
        
        # Hash long keys to prevent Redis key length issues
        if len(cache_key) > 200:
            key_hash = hashlib.md5(cache_key.encode()).hexdigest()
            cache_key = f"{prefix}:hash:{key_hash}"
        
        return cache_key
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache with Redis fallback to memory"""
        try:
            # Try Redis first
            if self.redis_client:
                try:
                    cached_data = await self.redis_client.get(key)
                    if cached_data:
                        self.cache_stats['hits'] += 1
                        return json.loads(cached_data)
                except Exception as e:
                    logger.warning(f"Redis get error: {e}")
            
            # Fallback to memory cache
            if key in self.memory_cache:
                cache_entry = self.memory_cache[key]
                
                # Check expiration
                if cache_entry['expires_at'] > datetime.utcnow():
                    self.cache_stats['hits'] += 1
                    return cache_entry['data']
                else:
                    # Remove expired entry
                    del self.memory_cache[key]
            
            self.cache_stats['misses'] += 1
            return None
            
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self.cache_stats['misses'] += 1
            return None
    
    async def set(self, key: str, value: Any, ttl_seconds: int = 300) -> bool:
        """Set value in cache with TTL"""
        try:
            serialized_value = json.dumps(value, default=str)
            
            # Try Redis first
            if self.redis_client:
                try:
                    await self.redis_client.setex(key, ttl_seconds, serialized_value)
                    self.cache_stats['sets'] += 1
                    return True
                except Exception as e:
                    logger.warning(f"Redis set error: {e}")
            
            # Fallback to memory cache
            expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
            self.memory_cache[key] = {
                'data': value,
                'expires_at': expires_at
            }
            
            # Memory cache cleanup (keep last 1000 entries)
            if len(self.memory_cache) > 1000:
                oldest_keys = sorted(self.memory_cache.keys())[:100]
                for old_key in oldest_keys:
                    del self.memory_cache[old_key]
            
            self.cache_stats['sets'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            deleted = False
            
            # Try Redis first
            if self.redis_client:
                try:
                    result = await self.redis_client.delete(key)
                    deleted = result > 0
                except Exception as e:
                    logger.warning(f"Redis delete error: {e}")
            
            # Also remove from memory cache
            if key in self.memory_cache:
                del self.memory_cache[key]
                deleted = True
            
            if deleted:
                self.cache_stats['deletes'] += 1
            
            return deleted
            
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern"""
        try:
            deleted_count = 0
            
            # Redis pattern invalidation
            if self.redis_client:
                try:
                    keys = await self.redis_client.keys(pattern)
                    if keys:
                        deleted_count += await self.redis_client.delete(*keys)
                except Exception as e:
                    logger.warning(f"Redis pattern delete error: {e}")
            
            # Memory cache pattern invalidation
            keys_to_delete = [key for key in self.memory_cache.keys() if pattern.replace('*', '') in key]
            for key in keys_to_delete:
                del self.memory_cache[key]
                deleted_count += 1
            
            self.cache_stats['deletes'] += deleted_count
            return deleted_count
            
        except Exception as e:
            logger.error(f"Cache pattern invalidation error: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.cache_stats,
            'hit_rate_percentage': round(hit_rate, 2),
            'memory_cache_size': len(self.memory_cache),
            'redis_available': self.redis_client is not None
        }
    
    async def cache_user_data(self, user_id: str, data_type: str, data: Any, ttl_seconds: int = 300):
        """Cache user-specific data with automatic key generation"""
        cache_key = self._generate_cache_key(f"user_data:{data_type}", user_id=user_id)
        await self.set(cache_key, data, ttl_seconds)
    
    async def get_user_data(self, user_id: str, data_type: str) -> Optional[Any]:
        """Get cached user-specific data"""
        cache_key = self._generate_cache_key(f"user_data:{data_type}", user_id=user_id)
        return await self.get(cache_key)
    
    async def invalidate_user_cache(self, user_id: str, data_type: str = None):
        """Invalidate all cached data for a user or specific data type"""
        if data_type:
            pattern = f"user_data:{data_type}:user:{user_id}*"
        else:
            pattern = f"user_data:*:user:{user_id}*"
        
        return await self.invalidate_pattern(pattern)

# Global cache service instance
cache_service = CacheService()

def cache_result(cache_key_prefix: str, ttl_seconds: int = 300, user_specific: bool = True):
    """
    Decorator for caching function results
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user_id if this is user-specific caching
            user_id = None
            if user_specific and args:
                # Assume first argument is user_id for user-specific functions
                user_id = str(args[0])
            
            # Generate cache key
            cache_key = cache_service._generate_cache_key(
                cache_key_prefix,
                user_id=user_id,
                **{k: str(v) for k, v in kwargs.items() if v is not None}
            )
            
            # Try to get from cache
            cached_result = await cache_service.get(cache_key)
            if cached_result is not None:
                logger.debug(f"🎯 Cache HIT: {cache_key}")
                return cached_result
            
            # Cache miss - execute function
            logger.debug(f"💿 Cache MISS: {cache_key}")
            result = await func(*args, **kwargs)
            
            # Cache the result
            await cache_service.set(cache_key, result, ttl_seconds)
            
            return result
        return wrapper
    return decorator

# Convenience decorators for common caching patterns
def cache_dashboard_data(ttl_seconds: int = 180):
    """Cache dashboard data for 3 minutes"""
    return cache_result("dashboard", ttl_seconds=ttl_seconds, user_specific=True)

def cache_user_projects(ttl_seconds: int = 300):
    """Cache user projects for 5 minutes"""
    return cache_result("projects", ttl_seconds=ttl_seconds, user_specific=True)

def cache_user_areas(ttl_seconds: int = 300):
    """Cache user areas for 5 minutes"""
    return cache_result("areas", ttl_seconds=ttl_seconds, user_specific=True)

def cache_user_pillars(ttl_seconds: int = 300):
    """Cache user pillars for 5 minutes"""
    return cache_result("pillars", ttl_seconds=ttl_seconds, user_specific=True)

def cache_insights_data(ttl_seconds: int = 600):
    """Cache insights data for 10 minutes"""
    return cache_result("insights", ttl_seconds=ttl_seconds, user_specific=True)