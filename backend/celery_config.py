"""
Celery Configuration for Aurum Life MVP v1.2
Robust task queue configuration with error handling and monitoring
"""

from celery import Celery, Task
from celery.signals import task_failure, task_retry, task_success
from kombu import Exchange, Queue
from config import settings
import logging
from datetime import timedelta
import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration

logger = logging.getLogger(__name__)

# Initialize Sentry for error tracking (if configured)
if settings.environment == "production" and hasattr(settings, 'sentry_dsn'):
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        integrations=[CeleryIntegration()],
        environment=settings.environment
    )

class CeleryConfig:
    """Celery configuration with best practices"""
    
    # Broker settings
    broker_url = settings.celery_broker_url
    result_backend = settings.celery_result_backend
    
    # Task settings
    task_serializer = 'json'
    result_serializer = 'json'
    accept_content = ['json']
    timezone = 'UTC'
    enable_utc = True
    
    # Task execution settings
    task_soft_time_limit = 300  # 5 minutes soft limit
    task_time_limit = 600  # 10 minutes hard limit
    task_acks_late = True  # Tasks acknowledged after completion
    worker_prefetch_multiplier = 1  # Prevent worker from prefetching too many tasks
    
    # Result backend settings
    result_expires = 3600  # Results expire after 1 hour
    result_persistent = True  # Store results persistently
    
    # Error handling
    task_reject_on_worker_lost = True
    task_ignore_result = False
    
    # Performance settings
    worker_max_tasks_per_child = 1000  # Restart worker after 1000 tasks (memory leak prevention)
    worker_disable_rate_limits = False
    
    # Queue configuration
    task_default_queue = 'default'
    task_default_exchange = 'default'
    task_default_exchange_type = 'direct'
    task_default_routing_key = 'default'
    
    task_queues = (
        Queue('default', Exchange('default'), routing_key='default'),
        Queue('scoring', Exchange('scoring'), routing_key='scoring'),
        Queue('notifications', Exchange('notifications'), routing_key='notifications'),
        Queue('maintenance', Exchange('maintenance'), routing_key='maintenance'),
    )
    
    task_routes = {
        'tasks.scoring.*': {'queue': 'scoring'},
        'tasks.notifications.*': {'queue': 'notifications'},
        'tasks.maintenance.*': {'queue': 'maintenance'},
    }
    
    # Beat schedule for periodic tasks
    beat_schedule = {
        'update-all-task-scores': {
            'task': 'tasks.scoring.update_all_task_scores',
            'schedule': timedelta(hours=1),  # Run every hour
            'options': {
                'queue': 'scoring',
                'priority': 5
            }
        },
        'cleanup-expired-sessions': {
            'task': 'tasks.maintenance.cleanup_expired_sessions',
            'schedule': timedelta(hours=6),  # Run every 6 hours
            'options': {
                'queue': 'maintenance',
                'priority': 3
            }
        },
        'generate-daily-stats': {
            'task': 'tasks.maintenance.generate_daily_stats',
            'schedule': timedelta(days=1),  # Run daily at midnight
            'options': {
                'queue': 'maintenance',
                'priority': 4
            }
        }
    }

# Create Celery app
app = Celery('aurum_life')
app.config_from_object(CeleryConfig)

class BaseTask(Task):
    """Base task with common error handling and logging"""
    
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 3, 'countdown': 60}
    retry_backoff = True
    retry_backoff_max = 600  # Max 10 minutes between retries
    retry_jitter = True  # Add randomness to retry delays
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure"""
        logger.error(
            f"Task {self.name}[{task_id}] failed: {exc}",
            extra={
                'task_id': task_id,
                'task_name': self.name,
                'args': args,
                'kwargs': kwargs,
                'exception': str(exc),
                'traceback': str(einfo)
            }
        )
        super().on_failure(exc, task_id, args, kwargs, einfo)
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Handle task retry"""
        logger.warning(
            f"Task {self.name}[{task_id}] retrying: {exc}",
            extra={
                'task_id': task_id,
                'task_name': self.name,
                'retry_count': self.request.retries
            }
        )
        super().on_retry(exc, task_id, args, kwargs, einfo)
    
    def on_success(self, retval, task_id, args, kwargs):
        """Handle task success"""
        logger.info(
            f"Task {self.name}[{task_id}] succeeded",
            extra={
                'task_id': task_id,
                'task_name': self.name,
                'duration': self.request.time_start and (time.time() - self.request.time_start)
            }
        )
        super().on_success(retval, task_id, args, kwargs)

# Set base task for all tasks
app.Task = BaseTask

# Signal handlers for monitoring
@task_failure.connect
def handle_task_failure(sender=None, task_id=None, exception=None, **kwargs):
    """Log task failures for monitoring"""
    logger.error(
        f"Task failure signal: {sender.name}[{task_id}] - {exception}",
        extra={
            'task_name': sender.name,
            'task_id': task_id,
            'exception_type': type(exception).__name__
        }
    )

@task_retry.connect
def handle_task_retry(sender=None, task_id=None, reason=None, **kwargs):
    """Log task retries for monitoring"""
    logger.warning(
        f"Task retry signal: {sender.name}[{task_id}] - {reason}",
        extra={
            'task_name': sender.name,
            'task_id': task_id,
            'retry_reason': str(reason)
        }
    )

@task_success.connect
def handle_task_success(sender=None, result=None, **kwargs):
    """Log task success for monitoring"""
    logger.debug(
        f"Task success signal: {sender.name}",
        extra={'task_name': sender.name}
    )

# Import time tracking
import time

# Health check task
@app.task(bind=True, name='health.check')
def health_check(self):
    """Simple health check task"""
    return {
        'status': 'healthy',
        'worker_id': self.request.id,
        'timestamp': datetime.utcnow().isoformat()
    }

# Utility functions
def get_task_info(task_id: str) -> dict:
    """Get information about a task"""
    result = app.AsyncResult(task_id)
    return {
        'task_id': task_id,
        'status': result.status,
        'result': result.result if result.successful() else None,
        'error': str(result.info) if result.failed() else None,
        'traceback': result.traceback
    }

def revoke_task(task_id: str, terminate: bool = False) -> bool:
    """Revoke a pending task"""
    try:
        app.control.revoke(task_id, terminate=terminate)
        logger.info(f"Revoked task {task_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to revoke task {task_id}: {e}")
        return False

# Import datetime at module level
from datetime import datetime