from celery import shared_task
from celery.schedules import crontab
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from datetime import datetime, timedelta
import logging
import requests
import json

from core.models import Schedule, Task, UserProfile, ProgressTracker, HabitCompletion
from .models import Notification, NotificationTemplate, NotificationPreference

logger = logging.getLogger(__name__)

class NotificationEngine:
    """Comprehensive notification engine with multiple delivery channels"""
    
    @staticmethod
    def send_push_notification(user, title, message, data=None):
        """Send Firebase Cloud Messaging push notification"""
        try:
            if not user.profile.fcm_token:
                return False
                
            # Firebase FCM implementation
            fcm_url = "https://fcm.googleapis.com/fcm/send"
            headers = {
                'Authorization': 'key=YOUR_FIREBASE_SERVER_KEY',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'to': user.profile.fcm_token,
                'notification': {
                    'title': title,
                    'body': message,
                    'icon': '/static/icons/icon-192x192.png',
                    'click_action': '/dashboard/'
                },
                'data': data or {}
            }
            
            response = requests.post(fcm_url, headers=headers, json=payload)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Push notification failed for {user.username}: {e}")
            return False
    
    @staticmethod
    def send_email_notification(user, title, message):
        """Send email notification"""
        try:
            if not user.email:
                return False
                
            html_message = render_to_string('notifications/email_template.html', {
                'title': title,
                'message': message,
                'user': user
            })
            
            send_mail(
                subject=title,
                message=message,
                from_email='notifications@productivityapp.com',
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            return True
        except Exception as e:
            logger.error(f"Email notification failed for {user.username}: {e}")
            return False
    
    @staticmethod
    def send_sms_notification(user, message):
        """Send SMS notification (Twilio integration)"""
        # Implement Twilio SMS integration
        pass
    
    @staticmethod
    def create_in_app_notification(user, title, message, notification_type='reminder', **kwargs):
        """Create in-app notification"""
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            channels=['in_app'],
            **kwargs
        )
        return notification

@shared_task
def schedule_daily_notifications():
    """Master scheduler for all daily notifications"""
    logger.info("Starting daily notification scheduling...")
    
    # Schedule all notification types
    send_morning_planning_notifications.delay()
    schedule_activity_reminders.delay()
    send_evening_review_reminders.delay()
    check_task_deadlines.delay()
    send_motivational_messages.delay()
    check_habit_completions.delay()
    
    logger.info("Daily notification scheduling completed")

@shared_task
def send_morning_planning_notifications():
    """Send morning planning notifications at 5:45 AM"""
    now = timezone.now()
    if now.hour == 5 and now.minute == 45:
        users = User.objects.filter(is_active=True)
        
        for user in users:
            pref = getattr(user, 'notification_preferences', None)
            if pref and not pref.push_enabled:
                continue
                
            # Get today's schedule
            today = now.strftime('%A')
            today_schedule = Schedule.objects.filter(user=user, day=today, is_active=True).order_by('start_time')
            
            # Create morning planning message
            if today_schedule.exists():
                first_activity = today_schedule.first()
                message = f"🌅 Good morning! You have {today_schedule.count()} activities today. First up: {first_activity.title} at {first_activity.start_time.strftime('%H:%M')}"
            else:
                message = "🌅 Good morning! You have a free day today. Perfect for working on your projects!"
            
            # Send notification
            NotificationEngine.create_in_app_notification(
                user=user,
                title="🌅 Morning Planning Time",
                message=message,
                notification_type='system'
            )
            
            # Send push notification if enabled
            if pref and pref.push_enabled:
                NotificationEngine.send_push_notification(user, "🌅 Morning Planning", message)

@shared_task
def schedule_activity_reminders():
    """Schedule activity reminders with lead time"""
    now = timezone.now()
    users = User.objects.filter(is_active=True)
    
    for user in users:
        pref = getattr(user, 'notification_preferences', None)
        if not pref:
            continue
            
        lead_time = pref.reminder_lead_time
        reminder_time = now + timedelta(minutes=lead_time)
        
        # Get activities starting at reminder_time
        current_day = now.strftime('%A')
        upcoming_activities = Schedule.objects.filter(
            user=user,
            day=current_day,
            start_time__hour=reminder_time.hour,
            start_time__minute=reminder_time.minute,
            is_active=True,
            notification_sent=False
        )
        
        for activity in upcoming_activities:
            # Check if user wants reminders for this activity type
            if not should_send_reminder(pref, activity.activity_type):
                continue
            
            title = f"🕒 Coming Up: {activity.title}"
            message = f"Starts in {lead_time} minutes at {activity.location or 'your scheduled location'}"
            
            # Create notification
            notification = NotificationEngine.create_in_app_notification(
                user=user,
                title=title,
                message=message,
                notification_type='reminder',
                related_schedule=activity
            )
            
            # Send via preferred channels
            if pref.push_enabled:
                NotificationEngine.send_push_notification(user, title, message)
            
            if pref.email_enabled:
                NotificationEngine.send_email_notification(user, title, message)
            
            # Mark as sent
            activity.notification_sent = True
            activity.save()

@shared_task
def send_activity_start_notifications():
    """Send notifications when activities actually start"""
    now = timezone.now()
    current_day = now.strftime('%A')
    
    current_activities = Schedule.objects.filter(
        day=current_day,
        start_time__hour=now.hour,
        start_time__minute=now.minute,
        is_active=True
    )
    
    for activity in current_activities:
        title = f"⏰ Now: {activity.title}"
        message = f"Time for {activity.get_activity_type_display()}! Focus and do your best. 🎯"
        
        NotificationEngine.create_in_app_notification(
            user=activity.user,
            title=title,
            message=message,
            notification_type='reminder',
            related_schedule=activity
        )

@shared_task
def send_evening_review_reminders():
    """Send evening review reminders at 9:30 PM"""
    now = timezone.now()
    if now.hour == 21 and now.minute == 30:
        users = User.objects.filter(is_active=True)
        
        for user in users:
            pref = getattr(user, 'notification_preferences', None)
            if pref and not pref.push_enabled:
                continue
            
            # Check if user has completed their daily review
            today_review = ProgressTracker.objects.filter(user=user, date=now.date()).exists()
            
            if not today_review:
                title = "🌙 Evening Review Time"
                message = "How did your day go? Complete your daily review and prepare for tomorrow."
                
                NotificationEngine.create_in_app_notification(
                    user=user,
                    title=title,
                    message=message,
                    notification_type='review'
                )

@shared_task
def check_task_deadlines():
    """Check for upcoming task deadlines"""
    now = timezone.now()
    tomorrow = now + timedelta(days=1)
    day_after = now + timedelta(days=2)
    
    # Tasks due tomorrow
    upcoming_tasks = Task.objects.filter(
        due_date=tomorrow.date(),
        status__in=['todo', 'in_progress']
    )
    
    for task in upcoming_tasks:
        title = "📅 Task Deadline Tomorrow"
        message = f"'{task.title}' is due tomorrow. Don't forget to complete it!"
        
        NotificationEngine.create_in_app_notification(
            user=task.user,
            title=title,
            message=message,
            notification_type='deadline',
            related_task=task
        )
    
    # Critical tasks due today
    critical_tasks = Task.objects.filter(
        due_date=now.date(),
        status__in=['todo', 'in_progress'],
        priority__in=['high', 'critical']
    )
    
    for task in critical_tasks:
        title = "🚨 Critical Task Due Today"
        message = f"'{task.title}' is due today! Priority: {task.get_priority_display()}"
        
        NotificationEngine.create_in_app_notification(
            user=task.user,
            title=title,
            message=message,
            notification_type='deadline',
            related_task=task,
            priority=5
        )

@shared_task
def send_motivational_messages():
    """Send random motivational messages throughout the day"""
    now = timezone.now()
    
    # Only send during active hours (8 AM - 8 PM)
    if 8 <= now.hour <= 20:
        motivational_messages = [
            "💪 You're doing great! Keep pushing forward!",
            "🚀 Progress, not perfection. Every step counts!",
            "🎯 Stay focused on your goals. You've got this!",
            "🔥 Your consistency is building your future!",
            "🌟 Believe in yourself and all that you are!",
        ]
        
        import random
        message = random.choice(motivational_messages)
        
        # Send to random active users (limit to 10% of users to avoid spam)
        users = User.objects.filter(is_active=True)
        sample_size = max(1, len(users) // 10)
        selected_users = random.sample(list(users), sample_size)
        
        for user in selected_users:
            NotificationEngine.create_in_app_notification(
                user=user,
                title="💪 Motivational Boost",
                message=message,
                notification_type='motivational'
            )

@shared_task
def check_habit_completions():
    """Check and notify about habit streaks"""
    now = timezone.now()
    today = now.date()
    
    from core.models import Habit, HabitCompletion
    
    users = User.objects.filter(is_active=True)
    
    for user in users:
        habits = Habit.objects.filter(user=user, is_active=True)
        
        for habit in habits:
            # Check if habit was completed today
            today_completion = HabitCompletion.objects.filter(
                habit=habit,
                date=today
            ).first()
            
            if not today_completion or not today_completion.completed:
                # Send reminder for incomplete habits
                if now.hour == 20:  # 8 PM reminder
                    title = "💪 Habit Reminder"
                    message = f"Don't forget to complete: {habit.name}"
                    
                    NotificationEngine.create_in_app_notification(
                        user=user,
                        title=title,
                        message=message,
                        notification_type='reminder'
                    )
            
            # Check for streak achievements
            if habit.current_streak > 0 and habit.current_streak % 7 == 0:
                title = "🔥 Streak Achievement!"
                message = f"Amazing! You've maintained '{habit.name}' for {habit.current_streak} days!"
                
                NotificationEngine.create_in_app_notification(
                    user=user,
                    title=title,
                    message=message,
                    notification_type='achievement'
                )

def should_send_reminder(preference, activity_type):
    """Check if user wants reminders for this activity type"""
    reminder_map = {
        'lecture': preference.enable_lecture_reminders,
        'lab': preference.enable_lab_reminders,
        'study': preference.enable_study_reminders,
        'workout': preference.enable_workout_reminders,
        'meal': preference.enable_meal_reminders,
        'relationship': preference.enable_relationship_reminders,
    }
    return reminder_map.get(activity_type, True)