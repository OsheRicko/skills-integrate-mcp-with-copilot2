"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from typing import List, Optional
import os
from pathlib import Path
import logging

# Import email-related modules
from email_preferences import (
    EmailPreferences,
    get_user_preferences,
    update_user_preferences,
    get_all_preferences,
    delete_user_preferences
)
from celery_tasks import (
    send_signup_confirmation_task,
    send_unregister_confirmation_task,
    send_new_activity_announcement_task,
    send_batch_emails_task
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
    },
    "GitHub Skills": {
        "description": "Learn practical coding and collaboration skills with GitHub - part of our GitHub Certifications program",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 25,
        "participants": []
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
async def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student
    activity["participants"].append(email)
    
    # Send confirmation email asynchronously (gracefully handle failures)
    try:
        send_signup_confirmation_task.delay(
            student_email=email,
            activity_name=activity_name,
            schedule=activity["schedule"],
            description=activity["description"]
        )
    except Exception as e:
        # Log error but don't fail the signup
        logger.warning(f"Failed to queue confirmation email: {e}")
    
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
async def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(email)
    
    # Send confirmation email asynchronously (gracefully handle failures)
    try:
        send_unregister_confirmation_task.delay(
            student_email=email,
            activity_name=activity_name,
            schedule=activity["schedule"]
        )
    except Exception as e:
        # Log error but don't fail the unregistration
        logger.warning(f"Failed to queue confirmation email: {e}")
    
    return {"message": f"Unregistered {email} from {activity_name}"}


# ============================================================================
# EMAIL PREFERENCES ENDPOINTS
# ============================================================================

@app.get("/email-preferences/{email}")
def get_email_preferences(email: str):
    """Get email preferences for a user"""
    preferences = get_user_preferences(email)
    return preferences


@app.put("/email-preferences/{email}")
def set_email_preferences(email: str, preferences: EmailPreferences):
    """Update email preferences for a user"""
    if email != preferences.email:
        raise HTTPException(
            status_code=400,
            detail="Email in path must match email in preferences"
        )
    updated_prefs = update_user_preferences(email, preferences)
    return {"message": "Preferences updated successfully", "preferences": updated_prefs}


@app.delete("/email-preferences/{email}")
def remove_email_preferences(email: str):
    """Delete email preferences for a user"""
    if delete_user_preferences(email):
        return {"message": "Preferences deleted successfully"}
    raise HTTPException(status_code=404, detail="Preferences not found")


@app.get("/email-preferences")
def list_all_preferences():
    """Get all user email preferences"""
    return get_all_preferences()


# ============================================================================
# EMAIL ANNOUNCEMENT ENDPOINTS
# ============================================================================

@app.post("/announcements/new-activity/{activity_name}")
async def announce_new_activity(
    activity_name: str,
    recipients: Optional[List[str]] = None
):
    """
    Send announcement email for a new activity.
    If recipients not specified, sends to all users with preferences enabled.
    """
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    activity = activities[activity_name]
    
    # If no recipients specified, get all users who want new activity emails
    if not recipients:
        all_prefs = get_all_preferences()
        recipients = [
            email for email, prefs in all_prefs.items()
            if prefs.new_activities and prefs.enabled
        ]
    
    if not recipients:
        return {"message": "No recipients to send to"}
    
    # Send announcement emails asynchronously (gracefully handle failures)
    try:
        send_new_activity_announcement_task.delay(
            recipients=recipients,
            activity_name=activity_name,
            schedule=activity["schedule"],
            description=activity["description"],
            max_participants=activity["max_participants"]
        )
    except Exception as e:
        # Log error but return success with warning
        logger.warning(f"Failed to queue announcement emails: {e}")
        return {
            "message": f"Could not queue announcement emails (task queue unavailable)",
            "activity": activity_name,
            "recipients_count": len(recipients),
            "warning": "Email service may not be available"
        }
    
    return {
        "message": f"Announcement emails queued for {len(recipients)} recipients",
        "activity": activity_name,
        "recipients_count": len(recipients)
    }


@app.post("/announcements/batch-email")
async def send_batch_announcement(
    recipients: List[str],
    subject: str,
    template_name: str,
    context: dict
):
    """
    Send batch announcement emails using a custom template.
    
    Args:
        recipients: List of email addresses
        subject: Email subject
        template_name: Name of the email template (without .html)
        context: Template context variables
    """
    if not recipients:
        raise HTTPException(status_code=400, detail="No recipients specified")
    
    # Send batch emails asynchronously (gracefully handle failures)
    try:
        send_batch_emails_task.delay(
            recipients=recipients,
            subject=subject,
            template_name=template_name,
            context=context
        )
    except Exception as e:
        # Log error but return informative message
        logger.warning(f"Failed to queue batch emails: {e}")
        return {
            "message": f"Could not queue batch emails (task queue unavailable)",
            "recipients_count": len(recipients),
            "warning": "Email service may not be available"
        }
    
    return {
        "message": f"Batch emails queued for {len(recipients)} recipients",
        "recipients_count": len(recipients)
    }


# ============================================================================
# EMAIL STATUS ENDPOINT
# ============================================================================

@app.get("/email-service/status")
def get_email_service_status():
    """Check if email service is configured and enabled"""
    from email_config import is_email_enabled
    
    enabled = is_email_enabled()
    return {
        "enabled": enabled,
        "message": "Email service is configured" if enabled else "Email service is not configured. Set MAIL_USERNAME and MAIL_PASSWORD environment variables."
    }

