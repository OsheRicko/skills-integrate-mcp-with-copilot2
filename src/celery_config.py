"""
Celery Configuration Module

This module sets up Celery for handling background tasks like
scheduled reminders and batch email sending.
"""

from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Celery
celery_app = Celery(
    "mergington_tasks",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Task result expiration (in seconds)
    result_expires=3600,
)

# Scheduled tasks configuration
celery_app.conf.beat_schedule = {
    # Send weekly digest every Monday at 8:00 AM
    "send-weekly-digest": {
        "task": "celery_tasks.send_weekly_digest_task",
        "schedule": crontab(hour=8, minute=0, day_of_week=1),
    },
    # Send daily reminders at 6:00 PM for next day activities
    "send-daily-reminders": {
        "task": "celery_tasks.send_daily_reminders_task",
        "schedule": crontab(hour=18, minute=0),
    },
}

# Auto-discover tasks
celery_app.autodiscover_tasks(["celery_tasks"])
