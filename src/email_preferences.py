"""
User Email Preferences Module

This module manages user preferences for email notifications,
including opt-in/opt-out settings and notification preferences.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, EmailStr
from enum import Enum


class EmailFrequency(str, Enum):
    """Email frequency options"""
    IMMEDIATE = "immediate"
    DAILY_DIGEST = "daily"
    WEEKLY_DIGEST = "weekly"
    DISABLED = "disabled"


class NotificationCategory(str, Enum):
    """Email notification categories"""
    SIGNUP_CONFIRMATION = "signup_confirmation"
    UNREGISTER_CONFIRMATION = "unregister_confirmation"
    ACTIVITY_CHANGES = "activity_changes"
    REMINDERS = "reminders"
    WEEKLY_DIGEST = "weekly_digest"
    NEW_ACTIVITIES = "new_activities"
    ATTENDANCE = "attendance"


class EmailPreferences(BaseModel):
    """User email preferences model"""
    email: EmailStr
    enabled: bool = True
    frequency: EmailFrequency = EmailFrequency.IMMEDIATE
    
    # Category-specific preferences (opt-in/out)
    signup_confirmation: bool = True
    unregister_confirmation: bool = True
    activity_changes: bool = True
    reminders: bool = True
    weekly_digest: bool = True
    new_activities: bool = True
    attendance: bool = True
    
    # Parent email for CC
    parent_email: Optional[EmailStr] = None
    parent_cc_enabled: bool = False
    
    # Digest preferences
    digest_only: bool = False  # If True, only send digest emails


# In-memory storage for user preferences
user_preferences: Dict[str, EmailPreferences] = {}


def get_user_preferences(email: str) -> EmailPreferences:
    """
    Get user email preferences, creating default if not exists.
    
    Args:
        email: User's email address
    
    Returns:
        EmailPreferences: User's email preferences
    """
    if email not in user_preferences:
        user_preferences[email] = EmailPreferences(email=email)
    return user_preferences[email]


def update_user_preferences(email: str, preferences: EmailPreferences) -> EmailPreferences:
    """
    Update user email preferences.
    
    Args:
        email: User's email address
        preferences: New preferences
    
    Returns:
        EmailPreferences: Updated preferences
    """
    user_preferences[email] = preferences
    return preferences


def should_send_email(email: str, category: NotificationCategory) -> bool:
    """
    Check if an email should be sent based on user preferences.
    
    Args:
        email: User's email address
        category: Email notification category
    
    Returns:
        bool: True if email should be sent
    """
    prefs = get_user_preferences(email)
    
    # Check if emails are globally disabled
    if not prefs.enabled or prefs.frequency == EmailFrequency.DISABLED:
        return False
    
    # Check if digest-only mode is enabled for non-digest emails
    if prefs.digest_only and category != NotificationCategory.WEEKLY_DIGEST:
        return False
    
    # Check category-specific preference
    category_map = {
        NotificationCategory.SIGNUP_CONFIRMATION: prefs.signup_confirmation,
        NotificationCategory.UNREGISTER_CONFIRMATION: prefs.unregister_confirmation,
        NotificationCategory.ACTIVITY_CHANGES: prefs.activity_changes,
        NotificationCategory.REMINDERS: prefs.reminders,
        NotificationCategory.WEEKLY_DIGEST: prefs.weekly_digest,
        NotificationCategory.NEW_ACTIVITIES: prefs.new_activities,
        NotificationCategory.ATTENDANCE: prefs.attendance,
    }
    
    return category_map.get(category, True)


def get_parent_email(email: str) -> Optional[str]:
    """
    Get parent email for CC if enabled.
    
    Args:
        email: Student's email address
    
    Returns:
        Optional[str]: Parent email if CC is enabled, None otherwise
    """
    prefs = get_user_preferences(email)
    if prefs.parent_cc_enabled and prefs.parent_email:
        return str(prefs.parent_email)
    return None


def get_all_preferences() -> Dict[str, EmailPreferences]:
    """
    Get all user preferences.
    
    Returns:
        Dict[str, EmailPreferences]: All user preferences
    """
    return user_preferences


def delete_user_preferences(email: str) -> bool:
    """
    Delete user preferences.
    
    Args:
        email: User's email address
    
    Returns:
        bool: True if preferences were deleted
    """
    if email in user_preferences:
        del user_preferences[email]
        return True
    return False
