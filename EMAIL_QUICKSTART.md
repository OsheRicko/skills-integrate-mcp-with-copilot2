# 📧 Email Notification System - Quick Start Guide

## What's New?

The Mergington High School API now includes a comprehensive email notification system that automatically sends emails for various events!

## 🎯 Features

### Automatic Emails
- ✉️ **Signup Confirmation** - Sent when students register for activities
- ✉️ **Unregister Confirmation** - Sent when students leave activities
- ✉️ **Activity Changes** - Notifications about schedule or activity changes
- ✉️ **Reminders** - 24-hour advance reminders for upcoming activities
- ✉️ **Weekly Digest** - Weekly summary of enrolled activities
- ✉️ **New Activities** - Announcements for newly available activities
- ✉️ **Parent Notifications** - CC parents on student emails

### User Control
- ⚙️ **Email Preferences** - Students can control what emails they receive
- 📊 **Frequency Options** - Immediate, daily digest, weekly digest, or disabled
- 👨‍👩‍👧 **Parent CC** - Option to copy parents on all emails
- 🎛️ **Category Control** - Opt-in/out of specific email types

## 🚀 Quick Start

### 1. Check Email Service Status

```bash
curl http://localhost:8000/email-service/status
```

**Response:**
```json
{
  "enabled": false,
  "message": "Email service is not configured. Set MAIL_USERNAME and MAIL_PASSWORD environment variables."
}
```

### 2. Configure Email Service (Optional)

Create a `.env` file in the project root:

```bash
# For Gmail
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_FROM=noreply@mergington.edu
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
```

**Note:** For Gmail, you need to use an [App Password](https://support.google.com/accounts/answer/185833).

### 3. Test the System

**Sign up for an activity:**
```bash
curl -X POST "http://localhost:8000/activities/Chess%20Club/signup?email=student@mergington.edu"
```

This will:
1. ✅ Add student to Chess Club
2. 📧 Queue a confirmation email (if configured)

## 📋 Managing Email Preferences

### Get Current Preferences

```bash
curl http://localhost:8000/email-preferences/student@mergington.edu
```

### Update Preferences

```bash
curl -X PUT http://localhost:8000/email-preferences/student@mergington.edu \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@mergington.edu",
    "enabled": true,
    "frequency": "weekly",
    "signup_confirmation": true,
    "reminders": false,
    "parent_email": "parent@example.com",
    "parent_cc_enabled": true
  }'
```

### Preference Options

**Frequency:**
- `"immediate"` - Send emails as events happen (default)
- `"daily"` - Daily digest of all events
- `"weekly"` - Weekly digest only
- `"disabled"` - No emails

**Categories** (true/false for each):
- `signup_confirmation` - Activity signup confirmations
- `unregister_confirmation` - Activity unregistration confirmations
- `activity_changes` - Activity change notifications
- `reminders` - Upcoming activity reminders
- `weekly_digest` - Weekly activity summary
- `new_activities` - New activity announcements
- `attendance` - Attendance notifications

**Parent Features:**
- `parent_email` - Parent's email address
- `parent_cc_enabled` - CC parent on student emails

## 📢 Sending Announcements

### Announce a New Activity

```bash
curl -X POST http://localhost:8000/announcements/new-activity/Chess%20Club
```

This sends an announcement email to all users who have opted in for new activity announcements.

### Send Batch Emails

```bash
curl -X POST http://localhost:8000/announcements/batch-email \
  -H "Content-Type: application/json" \
  -d '{
    "recipients": ["student1@mergington.edu", "student2@mergington.edu"],
    "subject": "Important Update",
    "template_name": "activity_change",
    "context": {
      "activity_name": "Chess Club",
      "change_description": "Meeting time has changed to 4:00 PM"
    }
  }'
```

## 🎨 Email Templates

7 professional HTML email templates are included:

1. **signup_confirmation.html** - Activity registration confirmation
2. **unregister_confirmation.html** - Unregistration confirmation
3. **activity_change.html** - Activity change notification
4. **reminder.html** - Upcoming activity reminder
5. **weekly_digest.html** - Weekly activity summary
6. **new_activity.html** - New activity announcement
7. **attendance_notification.html** - Attendance report for parents

All templates feature:
- 🎨 Professional design with school branding
- 📱 Mobile-responsive layout
- ✉️ Consistent styling
- 🎓 School colors (green: #1f883d)

## ⚙️ Advanced Setup (Optional)

### With Background Tasks (Celery + Redis)

For scheduled emails and better performance:

**1. Start Redis:**
```bash
docker run -d -p 6379:6379 redis
```

**2. Start Celery Worker:**
```bash
cd src
celery -A celery_config worker --loglevel=info
```

**3. Start Celery Beat (for scheduled tasks):**
```bash
cd src
celery -A celery_config beat --loglevel=info
```

### Scheduled Tasks

When Celery Beat is running:
- 📅 **Weekly Digest** - Every Monday at 8:00 AM UTC
- ⏰ **Daily Reminders** - Every day at 6:00 PM UTC

## 🧪 Testing

Run the test script to verify everything works:

```bash
python test_email_system.py
```

This tests:
- ✅ Email preferences system
- ✅ Email template rendering
- ✅ Email service configuration

## 📖 API Documentation

Visit the interactive API docs:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔍 Troubleshooting

### Emails Not Sending?

1. **Check service status:**
   ```bash
   curl http://localhost:8000/email-service/status
   ```

2. **Verify environment variables are set:**
   - `MAIL_USERNAME`
   - `MAIL_PASSWORD`

3. **For Gmail users:**
   - Enable 2-factor authentication
   - Generate an App Password
   - Use the App Password in `MAIL_PASSWORD`

### Background Tasks Not Working?

1. **Check Redis is running:**
   ```bash
   redis-cli ping
   # Should return: PONG
   ```

2. **Verify Celery worker is running**

3. **Check logs** for error messages

### Still Having Issues?

The system is designed to work without email configuration:
- Core features (signup/unregister) always work
- Email notifications are optional
- Check server logs for warnings

## 📚 Documentation

For detailed information, see:
- **EMAIL_SYSTEM_DOCS.md** - Comprehensive system documentation
- **IMPLEMENTATION_SUMMARY.md** - Implementation details
- **.env.example** - Configuration template

## 🎓 Example Workflows

### Student Registration Flow

1. Student signs up for activity via API
2. System adds student to activity
3. Confirmation email queued (if configured)
4. Parent receives CC (if enabled in preferences)

### Weekly Digest Flow

1. Celery Beat triggers weekly task (Mondays 8:00 AM)
2. System gathers each user's activities
3. Digest emails sent to users who opted in
4. Summary includes all registered activities for the week

### Announcement Flow

1. Admin announces new activity
2. System checks user preferences
3. Sends to users who opted in for new activity emails
4. Respects user frequency settings (immediate/digest)

## 💡 Tips

1. **Development**: Run without email configured - everything still works!
2. **Production**: Use a dedicated email service (SendGrid, Mailgun, AWS SES)
3. **Testing**: Use the test script to verify setup
4. **Customization**: Edit templates in `src/email_templates/`
5. **Monitoring**: Check logs for email delivery status

## 🔐 Security Notes

- ✅ Never commit `.env` file (it's in `.gitignore`)
- ✅ Use environment variables for credentials
- ✅ Use App Passwords for Gmail
- ✅ All dependencies security-scanned (0 vulnerabilities)

## 🎉 You're All Set!

The email notification system is ready to use. Start the server and try it out:

```bash
cd src
uvicorn app:app --reload
```

Then visit http://localhost:8000/docs to explore the API!

---

**Questions?** Check the comprehensive documentation in EMAIL_SYSTEM_DOCS.md
