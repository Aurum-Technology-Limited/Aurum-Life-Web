from celery import Celery
import os

# Create the Celery application instance
app = Celery('aurum_life')

# Configure Redis as message broker and result backend
app.conf.broker_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
app.conf.result_backend = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Optimize configuration for our scoring use case
app.conf.update(
    # Serialization settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Critical: Route scoring tasks to dedicated queue
    task_routes={
        'scoring_engine.recalculate_task_score': {'queue': 'scoring'},
        'scoring_engine.recalculate_dependent_tasks': {'queue': 'scoring'},
        'scoring_engine.recalculate_area_tasks': {'queue': 'scoring'},
        'scoring_engine.recalculate_project_tasks': {'queue': 'scoring'},
        # Multi-agent system queues
        'agent_base.route_message': {'queue': 'agent_orchestrator'},
        'agents.market_validation.*': {'queue': 'agent_market_validation'},
        'agents.product_architect.*': {'queue': 'agent_product_architect'},
        'agents.ai_engineering.*': {'queue': 'agent_ai_engineering'},
        'agents.business_intelligence.*': {'queue': 'agent_business_intelligence'},
        'agents.legal_protection.*': {'queue': 'agent_legal_protection'},
        'agents.operations.*': {'queue': 'agent_operations'},
        'agents.user_experience.*': {'queue': 'agent_user_experience'},
    },
    
    # Agent-specific queue configurations
    task_queue_max_priority=10,  # Support priority messaging
    worker_prefetch_multiplier=1,  # Process one message at a time for consistency
    task_acks_late=True,  # Acknowledge task only after completion
    worker_disable_rate_limits=False,
    
    # Retry and timeout settings for agents
    task_default_retry_delay=30,  # 30 seconds retry delay for agents
    task_max_retries=5,  # More retries for critical agent tasks
    task_soft_time_limit=300,  # 5 minutes soft limit
    task_time_limit=600,  # 10 minutes hard limit
    
    # Result settings
    result_expires=3600,  # Results expire after 1 hour
    
    # Monitoring and debugging
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # Enable task tracking for agent workflows
    task_track_started=True,
    task_publish_retry=True,
    task_publish_retry_policy={
        'max_retries': 3,
        'interval_start': 0,
        'interval_step': 0.2,
        'interval_max': 0.2,
    }
)

# Import tasks to register them
# Note: Import removed to avoid circular import - tasks will be discovered by Celery autodiscovery

if __name__ == '__main__':
    app.start()