"""
Celery Tasks Module

This module defines background tasks for email notifications,
including scheduled reminders and batch email sending.
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict
import logging
from celery_config import celery_app
from email_service import email_service
from email_preferences import should_send_email, NotificationCategory, get_parent_email

# Configure logging
logger = logging.getLogger(__name__)


# Helper to run async functions in Celery tasks
def run_async(coro):
    """Run async coroutine in sync context"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="celery_tasks.send_signup_confirmation_task")
def send_signup_confirmation_task(
    student_email: str,
    activity_name: str,
    schedule: str,
    description: str,
    student_name: str = None
):
    """
    Background task to send signup confirmation email.
    
    Args:
        student_email: Student's email address
        activity_name: Name of the activity
        schedule: Activity schedule
        description: Activity description
        student_name: Optional student name
    """
    if not should_send_email(student_email, NotificationCategory.SIGNUP_CONFIRMATION):
        return {"status": "skipped", "reason": "user preferences"}
    
    parent_email = get_parent_email(student_email)
    
    result = run_async(
        email_service.send_signup_confirmation(
            student_email=student_email,
            activity_name=activity_name,
            schedule=schedule,
            description=description,
            student_name=student_name,
            parent_email=parent_email
        )
    )
    return {"status": "sent" if result else "failed"}


@celery_app.task(name="celery_tasks.send_unregister_confirmation_task")
def send_unregister_confirmation_task(
    student_email: str,
    activity_name: str,
    schedule: str,
    student_name: str = None
):
    """
    Background task to send unregister confirmation email.
    
    Args:
        student_email: Student's email address
        activity_name: Name of the activity
        schedule: Activity schedule
        student_name: Optional student name
    """
    if not should_send_email(student_email, NotificationCategory.UNREGISTER_CONFIRMATION):
        return {"status": "skipped", "reason": "user preferences"}
    
    parent_email = get_parent_email(student_email)
    
    result = run_async(
        email_service.send_unregister_confirmation(
            student_email=student_email,
            activity_name=activity_name,
            schedule=schedule,
            student_name=student_name,
            parent_email=parent_email
        )
    )
    return {"status": "sent" if result else "failed"}


@celery_app.task(name="celery_tasks.send_activity_change_task")
def send_activity_change_task(
    recipients: List[str],
    activity_name: str,
    change_description: str,
    new_schedule: str = None
):
    """
    Background task to send activity change notification.
    
    Args:
        recipients: List of recipient email addresses
        activity_name: Name of the activity
        change_description: Description of what changed
        new_schedule: Optional new schedule
    """
    # Filter recipients based on preferences
    filtered_recipients = [
        email for email in recipients
        if should_send_email(email, NotificationCategory.ACTIVITY_CHANGES)
    ]
    
    if not filtered_recipients:
        return {"status": "skipped", "reason": "no recipients with enabled preferences"}
    
    result = run_async(
        email_service.send_activity_change_notification(
            recipients=filtered_recipients,
            activity_name=activity_name,
            change_description=change_description,
            new_schedule=new_schedule
        )
    )
    return {"status": "sent" if result else "failed", "recipients": len(filtered_recipients)}


@celery_app.task(name="celery_tasks.send_reminder_task")
def send_reminder_task(
    student_email: str,
    activity_name: str,
    schedule: str,
    next_session: str,
    student_name: str = None
):
    """
    Background task to send reminder email.
    
    Args:
        student_email: Student's email address
        activity_name: Name of the activity
        schedule: Activity schedule
        next_session: Date/time of next session
        student_name: Optional student name
    """
    if not should_send_email(student_email, NotificationCategory.REMINDERS):
        return {"status": "skipped", "reason": "user preferences"}
    
    result = run_async(
        email_service.send_reminder_email(
            student_email=student_email,
            activity_name=activity_name,
            schedule=schedule,
            next_session=next_session,
            student_name=student_name
        )
    )
    return {"status": "sent" if result else "failed"}


@celery_app.task(name="celery_tasks.send_weekly_digest_task")
def send_weekly_digest_task():
    """
    Scheduled task to send weekly digest to all users.
    This is a placeholder - actual implementation would query
    all users and their activities from the database.
    """
    # This is a simplified version
    # In production, you would:
    # 1. Query all users from database
    # 2. For each user, get their registered activities
    # 3. Send digest email
    
    logger.info(f"Weekly digest task executed at: {datetime.now()}")
    return {"status": "executed"}


@celery_app.task(name="celery_tasks.send_daily_reminders_task")
def send_daily_reminders_task():
    """
    Scheduled task to send daily reminders for upcoming activities.
    This is a placeholder - actual implementation would query
    activities scheduled for the next day.
    """
    # This is a simplified version
    # In production, you would:
    # 1. Query activities scheduled for tomorrow
    # 2. For each activity, get registered students
    # 3. Send reminder emails
    
    logger.info(f"Daily reminders task executed at: {datetime.now()}")
    return {"status": "executed"}


@celery_app.task(name="celery_tasks.send_new_activity_announcement_task")
def send_new_activity_announcement_task(
    recipients: List[str],
    activity_name: str,
    schedule: str,
    description: str,
    max_participants: int,
    portal_url: str = "http://localhost:8000"
):
    """
    Background task to send new activity announcement.
    
    Args:
        recipients: List of recipient email addresses
        activity_name: Name of the activity
        schedule: Activity schedule
        description: Activity description
        max_participants: Maximum number of participants
        portal_url: URL to the school portal
    """
    # Filter recipients based on preferences
    filtered_recipients = [
        email for email in recipients
        if should_send_email(email, NotificationCategory.NEW_ACTIVITIES)
    ]
    
    if not filtered_recipients:
        return {"status": "skipped", "reason": "no recipients with enabled preferences"}
    
    result = run_async(
        email_service.send_new_activity_announcement(
            recipients=filtered_recipients,
            activity_name=activity_name,
            schedule=schedule,
            description=description,
            max_participants=max_participants,
            portal_url=portal_url
        )
    )
    return {"status": "sent" if result else "failed", "recipients": len(filtered_recipients)}


@celery_app.task(name="celery_tasks.send_batch_emails_task")
def send_batch_emails_task(
    recipients: List[str],
    subject: str,
    template_name: str,
    context: Dict
):
    """
    Background task to send batch emails.
    
    Args:
        recipients: List of recipient email addresses
        subject: Email subject
        template_name: Template name
        context: Template context
    """
    results = []
    for recipient in recipients:
        result = run_async(
            email_service.send_email(
                recipients=[recipient],
                subject=subject,
                template_name=template_name,
                context=context
            )
        )
        results.append({"email": recipient, "sent": result})
    
    sent_count = sum(1 for r in results if r["sent"])
    return {
        "status": "completed",
        "total": len(recipients),
        "sent": sent_count,
        "failed": len(recipients) - sent_count
    }
