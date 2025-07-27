"""
Performance Monitoring Middleware
Provides real-time performance tracking and query analysis
Following industry standard observability patterns
"""

import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from functools import wraps
import asyncio

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """
    Performance monitoring for API endpoints and database operations
    Tracks response times, query counts, and performance bottlenecks
    """
    
    def __init__(self):
        self.metrics: Dict[str, List[Dict]] = {}
        self.query_counts: Dict[str, int] = {}
        self.slow_queries: List[Dict] = []
    
    def track_endpoint(self, endpoint: str):
        """Decorator to track endpoint performance"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                request_id = f"{endpoint}_{int(time.time() * 1000)}"
                
                logger.info(f"🚀 PERF: Starting {endpoint} (ID: {request_id})")
                
                try:
                    # Execute the function
                    result = await func(*args, **kwargs)
                    
                    # Calculate performance metrics
                    end_time = time.time()
                    duration_ms = (end_time - start_time) * 1000
                    
                    # Log performance
                    self._log_performance(endpoint, duration_ms, request_id, success=True)
                    
                    return result
                    
                except Exception as e:
                    end_time = time.time()
                    duration_ms = (end_time - start_time) * 1000
                    
                    # Log error performance
                    self._log_performance(endpoint, duration_ms, request_id, success=False, error=str(e))
                    
                    raise
                    
            return wrapper
        return decorator
    
    def track_query(self, query_type: str):
        """Decorator to track database query performance"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                
                try:
                    result = await func(*args, **kwargs)
                    
                    end_time = time.time()
                    duration_ms = (end_time - start_time) * 1000
                    
                    # Track query metrics
                    self._track_query_performance(query_type, duration_ms, success=True)
                    
                    return result
                    
                except Exception as e:
                    end_time = time.time()
                    duration_ms = (end_time - start_time) * 1000
                    
                    self._track_query_performance(query_type, duration_ms, success=False, error=str(e))
                    
                    raise
                    
            return wrapper
        return decorator
    
    def _log_performance(self, endpoint: str, duration_ms: float, request_id: str, success: bool, error: str = None):
        """Log endpoint performance with proper categorization"""
        
        # Categorize performance
        if duration_ms < 100:
            category = "EXCELLENT"
            emoji = "⚡"
        elif duration_ms < 300:
            category = "GOOD"
            emoji = "✅"
        elif duration_ms < 500:
            category = "ACCEPTABLE"
            emoji = "⚠️"
        elif duration_ms < 1000:
            category = "SLOW"
            emoji = "🐌"
        else:
            category = "VERY_SLOW"
            emoji = "🚨"
        
        # Store metrics
        if endpoint not in self.metrics:
            self.metrics[endpoint] = []
        
        metric = {
            'timestamp': datetime.utcnow().isoformat(),
            'duration_ms': duration_ms,
            'category': category,
            'success': success,
            'request_id': request_id,
            'error': error
        }
        
        self.metrics[endpoint].append(metric)
        
        # Keep only last 100 metrics per endpoint
        if len(self.metrics[endpoint]) > 100:
            self.metrics[endpoint] = self.metrics[endpoint][-100:]
        
        # Log with appropriate level
        if success:
            logger.info(f"{emoji} PERF: {endpoint} completed in {duration_ms:.2f}ms ({category}) - ID: {request_id}")
        else:
            logger.error(f"❌ PERF: {endpoint} failed in {duration_ms:.2f}ms - Error: {error} - ID: {request_id}")
        
        # Track slow queries
        if duration_ms > 500:
            self.slow_queries.append({
                'endpoint': endpoint,
                'duration_ms': duration_ms,
                'timestamp': datetime.utcnow().isoformat(),
                'error': error,
                'request_id': request_id
            })
            
            # Keep only last 50 slow queries
            if len(self.slow_queries) > 50:
                self.slow_queries = self.slow_queries[-50:]
    
    def _track_query_performance(self, query_type: str, duration_ms: float, success: bool, error: str = None):
        """Track database query performance"""
        
        # Increment query count
        if query_type not in self.query_counts:
            self.query_counts[query_type] = 0
        self.query_counts[query_type] += 1
        
        # Log query performance
        if duration_ms > 100:  # Log slow queries
            logger.warning(f"🔍 QUERY: {query_type} took {duration_ms:.2f}ms (Count: {self.query_counts[query_type]})")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        summary = {
            'endpoints': {},
            'query_counts': self.query_counts.copy(),
            'slow_queries': self.slow_queries[-10:],  # Last 10 slow queries
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Calculate endpoint statistics
        for endpoint, metrics in self.metrics.items():
            if not metrics:
                continue
                
            durations = [m['duration_ms'] for m in metrics if m['success']]
            
            if durations:
                summary['endpoints'][endpoint] = {
                    'count': len(metrics),
                    'success_count': len(durations),
                    'avg_duration_ms': sum(durations) / len(durations),
                    'min_duration_ms': min(durations),
                    'max_duration_ms': max(durations),
                    'last_duration_ms': durations[-1] if durations else None
                }
        
        return summary
    
    def detect_n1_patterns(self) -> List[str]:
        """Detect potential N+1 query patterns"""
        warnings = []
        
        # Check for high query counts
        for query_type, count in self.query_counts.items():
            if count > 10:  # More than 10 queries of same type might indicate N+1
                warnings.append(f"High query count: {query_type} executed {count} times")
        
        # Check for slow queries
        if len(self.slow_queries) > 5:
            warnings.append(f"Multiple slow queries detected: {len(self.slow_queries)} queries >500ms")
        
        return warnings
    
    def reset_metrics(self):
        """Reset all metrics (for testing)"""
        self.metrics.clear()
        self.query_counts.clear()
        self.slow_queries.clear()

# Global performance monitor instance
perf_monitor = PerformanceMonitor()

# Decorator shortcuts for common use
def track_endpoint_performance(endpoint: str):
    """Shortcut decorator for endpoint tracking"""
    return perf_monitor.track_endpoint(endpoint)

def track_query_performance(query_type: str):
    """Shortcut decorator for query tracking"""
    return perf_monitor.track_query(query_type)