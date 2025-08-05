"""
Celery configuration for background task processing.
"""

from celery import Celery
from app.core.config import settings

# Create Celery app instance
celery_app = Celery(
    "arbitrage_system",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        'app.tasks.scraping_tasks', 
        'app.tasks.analysis_tasks'
    ]
)

# Celery configuration
celery_app.conf.update(
    # Serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # Timezone
    timezone='UTC',
    enable_utc=True,
    
    # Task routing
    task_routes={
        'app.tasks.scraping_tasks.*': {'queue': 'scraping'},
        'app.tasks.analysis_tasks.*': {'queue': 'analysis'},
    },
    
    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
    result_backend_transport_options={
        'retry_policy': {
            'timeout': 5.0
        }
    },
    
    # Worker settings
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    
    # Beat schedule for periodic tasks
    beat_schedule={
        'update-prices-every-4-hours': {
            'task': 'app.tasks.scraping_tasks.update_all_prices',
            'schedule': 4 * 60 * 60,  # Every 4 hours
        },
        'analyze-opportunities-every-6-hours': {
            'task': 'app.tasks.analysis_tasks.analyze_all_products',
            'schedule': 6 * 60 * 60,  # Every 6 hours
        },
        'cleanup-expired-opportunities-daily': {
            'task': 'app.tasks.analysis_tasks.cleanup_expired_opportunities',
            'schedule': 24 * 60 * 60,  # Daily
        },
    },
    
    # Error handling
    task_reject_on_worker_lost=True,
    task_ignore_result=False,
)


# Task configuration
celery_app.conf.task_default_retry_delay = 60  # Retry after 60 seconds
celery_app.conf.task_max_retries = 3