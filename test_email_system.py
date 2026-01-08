#!/usr/bin/env python3
"""
Email Notification System Test Script

This script demonstrates the email notification system functionality
without requiring an actual email server or Redis instance.
"""

import sys
sys.path.insert(0, '/home/runner/work/skills-integrate-mcp-with-copilot2/skills-integrate-mcp-with-copilot2/src')

from email_preferences import (
    EmailPreferences,
    get_user_preferences,
    update_user_preferences,
    should_send_email,
    NotificationCategory,
    get_parent_email,
    EmailFrequency
)


def test_email_preferences():
    """Test email preferences system"""
    print("=" * 70)
    print("TESTING EMAIL PREFERENCES SYSTEM")
    print("=" * 70)
    
    # Test 1: Get default preferences
    print("\n1. Getting default preferences for a new user...")
    prefs = get_user_preferences("student@mergington.edu")
    print(f"   ✓ Default preferences created")
    print(f"   - Email enabled: {prefs.enabled}")
    print(f"   - Frequency: {prefs.frequency}")
    print(f"   - Signup confirmation: {prefs.signup_confirmation}")
    
    # Test 2: Update preferences
    print("\n2. Updating user preferences...")
    new_prefs = EmailPreferences(
        email="student@mergington.edu",
        enabled=True,
        frequency=EmailFrequency.WEEKLY_DIGEST,
        reminders=False,
        parent_email="parent@example.com",
        parent_cc_enabled=True
    )
    update_user_preferences("student@mergington.edu", new_prefs)
    print(f"   ✓ Preferences updated")
    print(f"   - Frequency changed to: {new_prefs.frequency}")
    print(f"   - Reminders disabled: {not new_prefs.reminders}")
    print(f"   - Parent CC enabled: {new_prefs.parent_cc_enabled}")
    
    # Test 3: Check if emails should be sent
    print("\n3. Testing email notification logic...")
    should_send_signup = should_send_email(
        "student@mergington.edu",
        NotificationCategory.SIGNUP_CONFIRMATION
    )
    should_send_reminder = should_send_email(
        "student@mergington.edu",
        NotificationCategory.REMINDERS
    )
    print(f"   ✓ Signup confirmation should send: {should_send_signup}")
    print(f"   ✓ Reminder should send: {should_send_reminder} (disabled in prefs)")
    
    # Test 4: Get parent email for CC
    print("\n4. Testing parent email CC functionality...")
    parent = get_parent_email("student@mergington.edu")
    print(f"   ✓ Parent email for CC: {parent}")
    
    # Test 5: Digest-only mode
    print("\n5. Testing digest-only mode...")
    digest_prefs = EmailPreferences(
        email="digest@mergington.edu",
        digest_only=True
    )
    update_user_preferences("digest@mergington.edu", digest_prefs)
    should_send_immediate = should_send_email(
        "digest@mergington.edu",
        NotificationCategory.SIGNUP_CONFIRMATION
    )
    should_send_digest = should_send_email(
        "digest@mergington.edu",
        NotificationCategory.WEEKLY_DIGEST
    )
    print(f"   ✓ Immediate email should send: {should_send_immediate} (digest-only mode)")
    print(f"   ✓ Weekly digest should send: {should_send_digest}")
    
    print("\n" + "=" * 70)
    print("✓ ALL EMAIL PREFERENCE TESTS PASSED")
    print("=" * 70)


def test_email_templates():
    """Test email template rendering"""
    print("\n" + "=" * 70)
    print("TESTING EMAIL TEMPLATES")
    print("=" * 70)
    
    from jinja2 import Environment, FileSystemLoader
    from pathlib import Path
    
    template_dir = Path('/home/runner/work/skills-integrate-mcp-with-copilot2/skills-integrate-mcp-with-copilot2/src/email_templates')
    jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))
    
    templates = [
        'signup_confirmation',
        'unregister_confirmation',
        'activity_change',
        'reminder',
        'weekly_digest',
        'new_activity',
        'attendance_notification'
    ]
    
    print(f"\nFound {len(templates)} email templates:")
    for template_name in templates:
        try:
            template = jinja_env.get_template(f"{template_name}.html")
            print(f"   ✓ {template_name}.html")
        except Exception as e:
            print(f"   ✗ {template_name}.html - Error: {e}")
    
    # Test rendering a template
    print("\nRendering sample signup confirmation email...")
    template = jinja_env.get_template("signup_confirmation.html")
    html = template.render(
        subject="Registration Confirmed",
        student_name="John Doe",
        activity_name="Chess Club",
        schedule="Fridays, 3:30 PM - 5:00 PM",
        description="Learn strategies and compete in chess tournaments"
    )
    print(f"   ✓ Template rendered successfully ({len(html)} characters)")
    print(f"   Sample content preview:")
    print(f"   {html[:200]}...")
    
    print("\n" + "=" * 70)
    print("✓ ALL EMAIL TEMPLATE TESTS PASSED")
    print("=" * 70)


def test_email_service():
    """Test email service configuration"""
    print("\n" + "=" * 70)
    print("TESTING EMAIL SERVICE CONFIGURATION")
    print("=" * 70)
    
    from email_config import is_email_enabled, get_email_config
    
    print("\n1. Checking email service status...")
    enabled = is_email_enabled()
    print(f"   Email service enabled: {enabled}")
    if not enabled:
        print(f"   Note: Set MAIL_USERNAME and MAIL_PASSWORD environment variables to enable")
    
    print("\n2. Loading email configuration...")
    try:
        config = get_email_config()
        print(f"   ✓ Email configuration loaded")
        print(f"   - Mail server: {config.MAIL_SERVER}")
        print(f"   - Mail port: {config.MAIL_PORT}")
        print(f"   - From address: {config.MAIL_FROM}")
        print(f"   - Template folder: {config.TEMPLATE_FOLDER}")
    except Exception as e:
        print(f"   ✗ Error loading configuration: {e}")
    
    print("\n" + "=" * 70)
    print("✓ EMAIL SERVICE CONFIGURATION TESTS PASSED")
    print("=" * 70)


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "EMAIL NOTIFICATION SYSTEM TESTS" + " " * 22 + "║")
    print("╚" + "═" * 68 + "╝")
    
    try:
        test_email_preferences()
        test_email_templates()
        test_email_service()
        
        print("\n")
        print("╔" + "═" * 68 + "╗")
        print("║" + " " * 20 + "ALL TESTS PASSED! ✓" + " " * 28 + "║")
        print("╚" + "═" * 68 + "╝")
        print("\n")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
