"""
Email Service Module

This module provides functions for sending various types of emails
to students, parents, and teachers for the activity management system.
"""

from typing import List, Optional, Dict, Any
from fastapi_mail import FastMail, MessageSchema, MessageType
from jinja2 import Environment, FileSystemLoader
import os
from pathlib import Path
from datetime import datetime
import logging

from email_config import get_email_config, is_email_enabled

# Configure logging
logger = logging.getLogger(__name__)


# Initialize Jinja2 environment for email templates
template_dir = Path(__file__).parent / "email_templates"
jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))


class EmailService:
    """Service for sending emails using FastAPI Mail"""
    
    def __init__(self):
        self.config = get_email_config()
        self.mail = FastMail(self.config)
        self.enabled = is_email_enabled()
    
    async def send_email(
        self,
        recipients: List[str],
        subject: str,
        template_name: str,
        context: Dict[str, Any],
        cc: Optional[List[str]] = None
    ) -> bool:
        """
        Send an email using a template.
        
        Args:
            recipients: List of recipient email addresses
            subject: Email subject
            template_name: Name of the template file (without .html)
            context: Template context variables
            cc: Optional list of CC recipients
        
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        if not self.enabled:
            logger.info(f"Email service disabled. Would send to {recipients}: {subject}")
            return False
        
        try:
            # Load and render template
            template = jinja_env.get_template(f"{template_name}.html")
            context['subject'] = subject
            html_content = template.render(**context)
            
            # Create message
            message = MessageSchema(
                subject=subject,
                recipients=recipients,
                body=html_content,
                subtype=MessageType.html,
                cc=cc
            )
            
            # Send email
            await self.mail.send_message(message)
            logger.info(f"Email sent successfully to {recipients}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {recipients}: {str(e)}")
            return False
    
    async def send_signup_confirmation(
        self,
        student_email: str,
        activity_name: str,
        schedule: str,
        description: str,
        student_name: Optional[str] = None,
        parent_email: Optional[str] = None
    ) -> bool:
        """
        Send activity signup confirmation email.
        
        Args:
            student_email: Student's email address
            activity_name: Name of the activity
            schedule: Activity schedule
            description: Activity description
            student_name: Optional student name
            parent_email: Optional parent email for CC
        
        Returns:
            bool: True if email was sent successfully
        """
        context = {
            'student_name': student_name,
            'activity_name': activity_name,
            'schedule': schedule,
            'description': description
        }
        
        recipients = [student_email]
        cc = [parent_email] if parent_email else None
        
        return await self.send_email(
            recipients=recipients,
            subject=f"Confirmed: {activity_name} Registration",
            template_name="signup_confirmation",
            context=context,
            cc=cc
        )
    
    async def send_unregister_confirmation(
        self,
        student_email: str,
        activity_name: str,
        schedule: str,
        student_name: Optional[str] = None,
        parent_email: Optional[str] = None
    ) -> bool:
        """
        Send activity unregistration confirmation email.
        
        Args:
            student_email: Student's email address
            activity_name: Name of the activity
            schedule: Activity schedule
            student_name: Optional student name
            parent_email: Optional parent email for CC
        
        Returns:
            bool: True if email was sent successfully
        """
        context = {
            'student_name': student_name,
            'activity_name': activity_name,
            'schedule': schedule
        }
        
        recipients = [student_email]
        cc = [parent_email] if parent_email else None
        
        return await self.send_email(
            recipients=recipients,
            subject=f"Unregistration Confirmed: {activity_name}",
            template_name="unregister_confirmation",
            context=context,
            cc=cc
        )
    
    async def send_activity_change_notification(
        self,
        recipients: List[str],
        activity_name: str,
        change_description: str,
        new_schedule: Optional[str] = None,
        student_name: Optional[str] = None
    ) -> bool:
        """
        Send notification about activity changes.
        
        Args:
            recipients: List of recipient email addresses
            activity_name: Name of the activity
            change_description: Description of what changed
            new_schedule: Optional new schedule
            student_name: Optional student name
        
        Returns:
            bool: True if email was sent successfully
        """
        context = {
            'student_name': student_name,
            'activity_name': activity_name,
            'change_description': change_description,
            'new_schedule': new_schedule
        }
        
        return await self.send_email(
            recipients=recipients,
            subject=f"Important Update: {activity_name}",
            template_name="activity_change",
            context=context
        )
    
    async def send_reminder_email(
        self,
        student_email: str,
        activity_name: str,
        schedule: str,
        next_session: str,
        student_name: Optional[str] = None
    ) -> bool:
        """
        Send reminder email for upcoming activity.
        
        Args:
            student_email: Student's email address
            activity_name: Name of the activity
            schedule: Activity schedule
            next_session: Date/time of next session
            student_name: Optional student name
        
        Returns:
            bool: True if email was sent successfully
        """
        context = {
            'student_name': student_name,
            'activity_name': activity_name,
            'schedule': schedule,
            'next_session': next_session
        }
        
        return await self.send_email(
            recipients=[student_email],
            subject=f"Reminder: {activity_name} Coming Up!",
            template_name="reminder",
            context=context
        )
    
    async def send_weekly_digest(
        self,
        student_email: str,
        activities: List[Dict[str, str]],
        week_start: str,
        week_end: str,
        student_name: Optional[str] = None
    ) -> bool:
        """
        Send weekly digest of activities.
        
        Args:
            student_email: Student's email address
            activities: List of activity dictionaries with name, schedule, description
            week_start: Week start date
            week_end: Week end date
            student_name: Optional student name
        
        Returns:
            bool: True if email was sent successfully
        """
        context = {
            'student_name': student_name,
            'activities': activities,
            'week_start': week_start,
            'week_end': week_end
        }
        
        return await self.send_email(
            recipients=[student_email],
            subject=f"Weekly Activity Digest: {week_start} - {week_end}",
            template_name="weekly_digest",
            context=context
        )
    
    async def send_new_activity_announcement(
        self,
        recipients: List[str],
        activity_name: str,
        schedule: str,
        description: str,
        max_participants: int,
        portal_url: str = "http://localhost:8000",
        student_name: Optional[str] = None
    ) -> bool:
        """
        Send announcement for new activity.
        
        Args:
            recipients: List of recipient email addresses
            activity_name: Name of the activity
            schedule: Activity schedule
            description: Activity description
            max_participants: Maximum number of participants
            portal_url: URL to the school portal
            student_name: Optional student name
        
        Returns:
            bool: True if email was sent successfully
        """
        context = {
            'student_name': student_name,
            'activity_name': activity_name,
            'schedule': schedule,
            'description': description,
            'max_participants': max_participants,
            'portal_url': portal_url
        }
        
        return await self.send_email(
            recipients=recipients,
            subject=f"New Activity Available: {activity_name}",
            template_name="new_activity",
            context=context
        )
    
    async def send_attendance_notification(
        self,
        recipient_email: str,
        student_name: str,
        activity_name: str,
        date: str,
        attendance_status: str,
        note: Optional[str] = None,
        recipient_name: Optional[str] = None
    ) -> bool:
        """
        Send attendance notification to parents/guardians.
        
        Args:
            recipient_email: Recipient's email address (usually parent)
            student_name: Student's name
            activity_name: Name of the activity
            date: Date of the activity
            attendance_status: Attendance status (Present, Absent, Late)
            note: Optional note about attendance
            recipient_name: Optional recipient name
        
        Returns:
            bool: True if email was sent successfully
        """
        context = {
            'recipient_name': recipient_name,
            'student_name': student_name,
            'activity_name': activity_name,
            'date': date,
            'attendance_status': attendance_status,
            'note': note
        }
        
        return await self.send_email(
            recipients=[recipient_email],
            subject=f"Attendance Notification: {student_name} - {activity_name}",
            template_name="attendance_notification",
            context=context
        )


# Global email service instance
email_service = EmailService()
