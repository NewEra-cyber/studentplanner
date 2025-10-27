from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'productivity_app.settings')

app = Celery('productivity_app')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Comprehensive beat schedule
app.conf.beat_schedule = {
    # Morning routines
    'morning-planning-notifications': {
        'task': 'notifications.tasks.send_morning_planning_notifications',
        'schedule': crontab(hour=5, minute=45),
    },
    
    # Activity reminders (every minute for precision)
    'activity-reminders': {
        'task': 'notifications.tasks.schedule_activity_reminders', 
        'schedule': crontab(minute='*'),
    },
    
    # Activity start notifications
    'activity-start-notifications': {
        'task': 'notifications.tasks.send_activity_start_notifications',
        'schedule': crontab(minute='*'),
    },
    
    # Evening routines
    'evening-review-reminders': {
        'task': 'notifications.tasks.send_evening_review_reminders',
        'schedule': crontab(hour=21, minute=30),
    },
    
    # Task management
    'task-deadline-check': {
        'task': 'notifications.tasks.check_task_deadlines',
        'schedule': crontab(hour=8, minute=0),  # 8:00 AM
    },
    
    # Habit tracking
    'habit-completion-check': {
        'task': 'notifications.tasks.check_habit_completions',
        'schedule': crontab(hour=20, minute=0),  # 8:00 PM
    },
    
    # Motivational messages (3 times daily)
    'motivational-messages-1': {
        'task': 'notifications.tasks.send_motivational_messages',
        'schedule': crontab(hour=10, minute=0),  # 10:00 AM
    },
    'motivational-messages-2': {
        'task': 'notifications.tasks.send_motivational_messages', 
        'schedule': crontab(hour=14, minute=0),  # 2:00 PM
    },
    'motivational-messages-3': {
        'task': 'notifications.tasks.send_motivational_messages',
        'schedule': crontab(hour=17, minute=0),  # 5:00 PM
    },
    
    # Weekly review (Sunday 2:00 PM)
    'weekly-review-reminder': {
        'task': 'notifications.tasks.send_weekly_review_reminder',
        'schedule': crontab(day_of_week=0, hour=14, minute=0),
    },
    
    # Relationship time reminders (Daily 9:00 PM)
    'relationship-reminders': {
        'task': 'notifications.tasks.send_relationship_reminder',
        'schedule': crontab(hour=21, minute=0),
    },
    
    # Daily notification scheduler (6:00 AM)
    'daily-notification-scheduler': {
        'task': 'notifications.tasks.schedule_daily_notifications',
        'schedule': crontab(hour=6, minute=0),
    },
}