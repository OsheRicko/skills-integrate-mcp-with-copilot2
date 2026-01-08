# Email Notification System Documentation

## Overview

The Mergington High School API now includes a comprehensive email notification system that sends automated emails for various events related to extracurricular activities.

## Features

### 1. Transactional Emails
- **Activity Signup Confirmation**: Sent when a student registers for an activity
- **Activity Unregistration Confirmation**: Sent when a student unregisters from an activity

### 2. Notification Emails
- **Activity Changes**: Sent when activity details (schedule, location, etc.) are modified
- **Activity Cancellations**: Notifications about cancelled activities

### 3. Reminder Emails
- **Upcoming Activity Reminders**: Sent 24 hours before scheduled activities
- **Weekly Activity Digest**: Weekly summary of registered activities

### 4. Announcement Emails
- **New Activity Announcements**: Sent when new activities become available
- **General Announcements**: Custom batch emails for important updates

### 5. Parent Notifications
- **Attendance Notifications**: Sent to parents about student attendance
- **CC on Student Emails**: Optional parent email copy on all student communications

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and configure your email service:

```bash
cp .env.example .env
```

Edit `.env` with your email credentials:

```
MAIL_USERNAME=your_email@example.com
MAIL_PASSWORD=your_email_password
MAIL_FROM=noreply@mergington.edu
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
```

### 3. Start Redis (Required for Background Tasks)

```bash
# Using Docker
docker run -d -p 6379:6379 redis

# Or install Redis locally
# macOS: brew install redis && redis-server
# Ubuntu: sudo apt-get install redis-server && redis-server
```

### 4. Start Celery Worker (Optional for Background Tasks)

```bash
cd src
celery -A celery_config worker --loglevel=info
```

### 5. Start Celery Beat (Optional for Scheduled Tasks)

```bash
cd src
celery -A celery_config beat --loglevel=info
```

### 6. Start the Application

```bash
cd src
uvicorn app:app --reload
```

## API Endpoints

### Email Preferences

#### Get User Preferences
```
GET /email-preferences/{email}
```

Returns the email preferences for a specific user.

#### Update User Preferences
```
PUT /email-preferences/{email}
```

**Request Body:**
```json
{
  "email": "student@mergington.edu",
  "enabled": true,
  "frequency": "immediate",
  "signup_confirmation": true,
  "unregister_confirmation": true,
  "activity_changes": true,
  "reminders": true,
  "weekly_digest": true,
  "new_activities": true,
  "attendance": true,
  "parent_email": "parent@example.com",
  "parent_cc_enabled": true,
  "digest_only": false
}
```

#### Delete User Preferences
```
DELETE /email-preferences/{email}
```

#### List All Preferences
```
GET /email-preferences
```

### Announcements

#### Announce New Activity
```
POST /announcements/new-activity/{activity_name}
```

**Query Parameters:**
- `recipients` (optional): List of email addresses to send to

Sends announcement emails about a new activity. If no recipients specified, sends to all users who have opted in for new activity announcements.

#### Send Batch Email
```
POST /announcements/batch-email
```

**Request Body:**
```json
{
  "recipients": ["student1@mergington.edu", "student2@mergington.edu"],
  "subject": "Important Update",
  "template_name": "activity_change",
  "context": {
    "activity_name": "Chess Club",
    "change_description": "Meeting time has changed",
    "new_schedule": "Fridays, 4:00 PM - 5:30 PM"
  }
}
```

### Email Service Status

#### Check Email Service Status
```
GET /email-service/status
```

Returns whether the email service is properly configured and enabled.

## Email Templates

All email templates are located in `src/email_templates/` and use Jinja2 templating.

### Available Templates

1. **base.html** - Base template with school branding
2. **signup_confirmation.html** - Activity signup confirmation
3. **unregister_confirmation.html** - Activity unregistration confirmation
4. **activity_change.html** - Activity change notification
5. **reminder.html** - Upcoming activity reminder
6. **weekly_digest.html** - Weekly activity digest
7. **new_activity.html** - New activity announcement
8. **attendance_notification.html** - Attendance notification for parents

### Customizing Templates

You can customize any template by editing the HTML file. All templates extend the base template and use the school's color scheme (green: #1f883d).

## User Preferences System

### Email Frequency Options

- **immediate**: Send emails as events occur (default)
- **daily**: Send daily digest of all events
- **weekly**: Send weekly digest only
- **disabled**: No emails sent

### Notification Categories

Users can opt-in or opt-out of specific types of emails:

- Signup confirmations
- Unregistration confirmations
- Activity changes
- Reminders
- Weekly digest
- New activity announcements
- Attendance notifications

### Parent CC Feature

Parents can be CC'd on student emails by:
1. Setting `parent_email` in user preferences
2. Enabling `parent_cc_enabled`

## Background Tasks

### Celery Tasks

The system uses Celery for asynchronous email sending and scheduled tasks:

1. **send_signup_confirmation_task**: Sends signup confirmation emails
2. **send_unregister_confirmation_task**: Sends unregistration confirmation emails
3. **send_activity_change_task**: Sends activity change notifications
4. **send_reminder_task**: Sends reminder emails
5. **send_weekly_digest_task**: Scheduled task for weekly digests (Mondays at 8:00 AM)
6. **send_daily_reminders_task**: Scheduled task for daily reminders (Daily at 6:00 PM)
7. **send_new_activity_announcement_task**: Sends new activity announcements
8. **send_batch_emails_task**: Sends batch emails

### Scheduled Tasks

- **Weekly Digest**: Sent every Monday at 8:00 AM UTC
- **Daily Reminders**: Sent every day at 6:00 PM UTC for next-day activities

## Email Service Configuration

### Supported Email Providers

#### Gmail
```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_TLS=True
```

**Note**: For Gmail, you need to use an App Password if 2FA is enabled.

#### SendGrid
```
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USERNAME=apikey
MAIL_PASSWORD=your_sendgrid_api_key
```

#### Other SMTP Services

The system works with any SMTP-compatible email service. Configure the appropriate SMTP server, port, and credentials.

## Testing

### Testing Without Email Service

If email credentials are not configured, the system will log email actions to the console instead of sending actual emails. This is useful for development and testing.

### Testing Email Delivery

1. Configure email credentials in `.env`
2. Check email service status:
   ```bash
   curl http://localhost:8000/email-service/status
   ```
3. Test signup with email notification:
   ```bash
   curl -X POST "http://localhost:8000/activities/Chess%20Club/signup?email=test@example.com"
   ```
4. Check your email for the confirmation

## Security Considerations

1. **Never commit `.env` file**: The `.env` file contains sensitive credentials and is in `.gitignore`
2. **Use environment variables**: All sensitive configuration uses environment variables
3. **Use App Passwords**: For Gmail and similar services, use app-specific passwords
4. **Email validation**: Email addresses are validated using Pydantic EmailStr
5. **Rate limiting**: Consider implementing rate limiting for email endpoints in production

## Troubleshooting

### Emails Not Sending

1. Check email service status: `GET /email-service/status`
2. Verify environment variables are set correctly
3. Check Celery worker is running (if using background tasks)
4. Check application logs for error messages
5. Verify SMTP credentials and server settings

### Celery Tasks Not Running

1. Ensure Redis is running: `redis-cli ping`
2. Check Celery worker is started
3. Check Celery logs for errors
4. Verify `CELERY_BROKER_URL` is correct in `.env`

### Templates Not Found

1. Verify templates are in `src/email_templates/`
2. Check template file names match (e.g., `signup_confirmation.html`)
3. Ensure template folder path is correct in `email_config.py`

## Production Deployment

### Recommendations

1. **Use a dedicated email service**: SendGrid, Mailgun, AWS SES for better deliverability
2. **Set up monitoring**: Monitor email delivery rates and failures
3. **Implement rate limiting**: Prevent abuse of email endpoints
4. **Use a task queue**: Deploy Celery workers for better performance
5. **Configure email limits**: Set daily/hourly email limits to prevent spam
6. **Enable SPF/DKIM**: Configure proper email authentication
7. **Use Redis persistence**: Configure Redis to persist task queue

## Future Enhancements

- Email delivery status tracking
- Email open/click tracking
- Unsubscribe links in emails
- Email bounce handling
- Advanced template customization UI
- Multi-language email support
- Email scheduling (send at specific times)
- Email analytics dashboard
