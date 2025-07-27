"""
MVP Performance Monitor for Aurum Life v1.1
Tracks API response times and database query performance
"""

from fastapi import Request, Response
from typing import Callable
import time
import logging
from datetime import datetime
import asyncio
from collections import deque
import statistics

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Tracks API and database performance metrics"""
    
    def __init__(self, window_size: int = 1000):
        # Rolling window of response times
        self.response_times = deque(maxlen=window_size)
        self.slow_endpoints = {}
        self.endpoint_stats = {}
        
    def add_response_time(self, endpoint: str, duration: float):
        """Record a response time"""
        self.response_times.append(duration)
        
        # Track by endpoint
        if endpoint not in self.endpoint_stats:
            self.endpoint_stats[endpoint] = deque(maxlen=100)
        self.endpoint_stats[endpoint].append(duration)
        
        # Track slow requests
        if duration > 0.15:  # 150ms threshold
            if endpoint not in self.slow_endpoints:
                self.slow_endpoints[endpoint] = 0
            self.slow_endpoints[endpoint] += 1
            
    def get_p95(self) -> float:
        """Get 95th percentile response time"""
        if not self.response_times:
            return 0.0
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * 0.95)
        return sorted_times[index]
        
    def get_p99(self) -> float:
        """Get 99th percentile response time"""
        if not self.response_times:
            return 0.0
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * 0.99)
        return sorted_times[index]
        
    def get_average(self) -> float:
        """Get average response time"""
        if not self.response_times:
            return 0.0
        return statistics.mean(self.response_times)
        
    def get_endpoint_stats(self, endpoint: str) -> dict:
        """Get statistics for a specific endpoint"""
        if endpoint not in self.endpoint_stats or not self.endpoint_stats[endpoint]:
            return {"average": 0, "p95": 0, "count": 0}
            
        times = list(self.endpoint_stats[endpoint])
        sorted_times = sorted(times)
        p95_index = int(len(sorted_times) * 0.95)
        
        return {
            "average": statistics.mean(times),
            "p95": sorted_times[p95_index],
            "count": len(times),
            "slow_count": self.slow_endpoints.get(endpoint, 0)
        }
        
    def get_summary(self) -> dict:
        """Get performance summary"""
        return {
            "overall": {
                "average": self.get_average(),
                "p95": self.get_p95(),
                "p99": self.get_p99(),
                "total_requests": len(self.response_times)
            },
            "slow_endpoints": dict(self.slow_endpoints),
            "endpoint_details": {
                endpoint: self.get_endpoint_stats(endpoint)
                for endpoint in self.endpoint_stats
            }
        }

# Global performance monitor instance
perf_monitor = PerformanceMonitor()

async def performance_middleware(request: Request, call_next: Callable) -> Response:
    """
    Middleware to track API performance
    Logs warnings for requests exceeding 150ms
    """
    # Skip performance tracking for static files and health checks
    if request.url.path.startswith("/static") or request.url.path == "/health":
        return await call_next(request)
        
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Record metrics
    endpoint = f"{request.method} {request.url.path}"
    perf_monitor.add_response_time(endpoint, duration)
    
    # Log slow requests
    if duration > 0.15:  # 150ms
        logger.warning(
            f"SLOW REQUEST: {endpoint} took {duration:.3f}s "
            f"(Target: <0.15s)"
        )
        
    # Add performance headers
    response.headers["X-Response-Time"] = f"{duration:.3f}"
    response.headers["X-P95-Time"] = f"{perf_monitor.get_p95():.3f}"
    
    # Log critical performance issues
    if duration > 0.5:  # 500ms is critical
        logger.error(
            f"CRITICAL PERFORMANCE: {endpoint} took {duration:.3f}s"
        )
        
    return response

# Database query performance tracking
class DatabasePerformanceTracker:
    """Tracks MongoDB query performance"""
    
    def __init__(self):
        self.query_times = {}
        
    async def track_query(self, collection: str, operation: str, query: dict = None):
        """Decorator to track database query performance"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                
                try:
                    result = await func(*args, **kwargs)
                    duration = time.time() - start_time
                    
                    # Track query time
                    key = f"{collection}.{operation}"
                    if key not in self.query_times:
                        self.query_times[key] = deque(maxlen=100)
                    self.query_times[key].append(duration)
                    
                    # Log slow queries
                    if duration > 0.05:  # 50ms for DB queries
                        logger.warning(
                            f"SLOW QUERY: {key} took {duration:.3f}s"
                        )
                        
                    return result
                    
                except Exception as e:
                    duration = time.time() - start_time
                    logger.error(
                        f"QUERY ERROR: {key} failed after {duration:.3f}s - {e}"
                    )
                    raise
                    
            return wrapper
        return decorator
        
    def get_query_stats(self) -> dict:
        """Get database query statistics"""
        stats = {}
        for key, times in self.query_times.items():
            if times:
                sorted_times = sorted(times)
                p95_index = int(len(sorted_times) * 0.95)
                stats[key] = {
                    "average": statistics.mean(times),
                    "p95": sorted_times[p95_index],
                    "count": len(times)
                }
        return stats

# Global database tracker
db_perf_tracker = DatabasePerformanceTracker()

# Performance monitoring endpoints
from fastapi import APIRouter

perf_router = APIRouter(prefix="/api/performance", tags=["monitoring"])

@perf_router.get("/summary")
async def get_performance_summary():
    """Get current performance metrics"""
    return {
        "api_performance": perf_monitor.get_summary(),
        "database_performance": db_perf_tracker.get_query_stats(),
        "timestamp": datetime.utcnow()
    }

@perf_router.get("/health")
async def health_check():
    """Health check with performance status"""
    p95 = perf_monitor.get_p95()
    status = "healthy" if p95 < 0.15 else "degraded"
    
    return {
        "status": status,
        "p95_response_time": p95,
        "target_p95": 0.15,
        "timestamp": datetime.utcnow()
    }

# Scheduled performance reporting
async def log_performance_metrics():
    """Log performance metrics every 5 minutes"""
    while True:
        await asyncio.sleep(300)  # 5 minutes
        
        summary = perf_monitor.get_summary()
        p95 = summary["overall"]["p95"]
        
        if p95 > 0.15:
            logger.warning(
                f"PERFORMANCE ALERT: P95 response time is {p95:.3f}s "
                f"(exceeds 150ms target)"
            )
            
        logger.info(
            f"Performance Summary - "
            f"P95: {p95:.3f}s, "
            f"Average: {summary['overall']['average']:.3f}s, "
            f"Requests: {summary['overall']['total_requests']}"
        )

# Start performance monitoring on app startup
def start_performance_monitoring():
    """Initialize performance monitoring background tasks"""
    asyncio.create_task(log_performance_metrics())