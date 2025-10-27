from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import (
    User, Schedule, Task, ProgressTracker, SmartSuggestion,
    Notification, AnalyticsDashboard
)
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_scheduled_notifications():
    """Send scheduled notifications to users"""
    now = timezone.now()
    
    # Find notifications scheduled for now or past
    notifications = Notification.objects.filter(
        scheduled_for__lte=now,
        is_sent=False,
        is_active=True
    ).select_related('user')
    
    for notification in notifications:
        try:
            # Send notification based on channels
            if 'push' in notification.channels:
                send_push_notification.delay(notification.id)
            
            if 'email' in notification.channels:
                send_email_notification.delay(notification.id)
            
            # Mark as sent
            notification.is_sent = True
            notification.sent_at = timezone.now()
            notification.save()
            
            logger.info(f"Sent notification: {notification.title}")
            
        except Exception as e:
            logger.error(f"Error sending notification {notification.id}: {str(e)}")

@shared_task
def send_push_notification(notification_id):
    """Send push notification"""
    try:
        notification = Notification.objects.get(id=notification_id)
        # Implement your push notification service (FCM, OneSignal, etc.)
        # This is a placeholder implementation
        logger.info(f"Push notification sent: {notification.title}")
        
    except Notification.DoesNotExist:
        logger.error(f"Notification {notification_id} not found")

@shared_task
def send_email_notification(notification_id):
    """Send email notification"""
    try:
        notification = Notification.objects.get(id=notification_id)
        
        send_mail(
            subject=notification.title,
            message=notification.message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notification.user.email],
            fail_silently=False,
        )
        
        logger.info(f"Email notification sent to {notification.user.email}")
        
    except Exception as e:
        logger.error(f"Error sending email notification: {str(e)}")

@shared_task
def generate_smart_suggestions():
    """Generate AI-powered smart suggestions for all users"""
    users = User.objects.all()
    
    for user in users:
        try:
            # Analyze user's recent activity
            recent_progress = ProgressTracker.objects.filter(
                user=user,
                date__gte=timezone.now().date() - timedelta(days=7)
            ).order_by('-date')
            
            if not recent_progress:
                continue
            
            # Calculate averages
            avg_productivity = sum(p.productivity_score for p in recent_progress) / len(recent_progress)
            avg_study_hours = sum(p.study_hours for p in recent_progress) / len(recent_progress)
            
            # Generate suggestions based on patterns
            if avg_productivity < 50:
                SmartSuggestion.objects.create(
                    user=user,
                    suggestion_type='productivity_tip',
                    title='Boost Your Productivity',
                    description=f'Your average productivity is {avg_productivity:.1f}%. Try time blocking technique.',
                    confidence_score=0.8
                )
            
            if avg_study_hours < 3:
                SmartSuggestion.objects.create(
                    user=user,
                    suggestion_type='study_recommendation',
                    title='Increase Study Consistency',
                    description=f'You study {avg_study_hours:.1f} hours daily. Consider adding focused study sessions.',
                    confidence_score=0.7
                )
            
            # Check for overdue tasks
            overdue_tasks = Task.objects.filter(
                user=user,
                due_date__lt=timezone.now().date(),
                status__in=['todo', 'in_progress']
            )
            
            if overdue_tasks.exists():
                SmartSuggestion.objects.create(
                    user=user,
                    suggestion_type='time_optimization',
                    title='Overdue Tasks Alert',
                    description=f'You have {overdue_tasks.count()} overdue tasks. Consider rescheduling or prioritizing.',
                    confidence_score=0.9
                )
                
        except Exception as e:
            logger.error(f"Error generating suggestions for {user.username}: {str(e)}")

@shared_task
def update_productivity_analytics():
    """Update productivity analytics for all users"""
    today = timezone.now().date()
    users = User.objects.all()
    
    for user in users:
        try:
            # Get or create today's analytics
            analytics, created = AnalyticsDashboard.objects.get_or_create(
                user=user,
                date=today
            )
            
            # Calculate today's metrics
            today_progress = ProgressTracker.objects.filter(user=user, date=today).first()
            
            if today_progress:
                analytics.total_study_time = timedelta(hours=float(today_progress.study_hours))
                analytics.completed_tasks = today_progress.tasks_completed
                analytics.productivity_score = today_progress.productivity_score
                analytics.workout_time = timedelta(hours=1) if today_progress.workout_completed else timedelta(0)
            
            # Calculate weekly averages
            week_ago = today - timedelta(days=7)
            weekly_progress = ProgressTracker.objects.filter(
                user=user,
                date__range=[week_ago, today]
            )
            
            if weekly_progress:
                avg_productivity = weekly_progress.aggregate(models.Avg('productivity_score'))['productivity_score__avg'] or 0
                total_study_hours = weekly_progress.aggregate(Sum('study_hours'))['study_hours__sum'] or 0
                
                analytics.metadata = {
                    'weekly_avg_productivity': avg_productivity,
                    'weekly_total_study_hours': total_study_hours,
                    'analysis_date': timezone.now().isoformat()
                }
            
            analytics.save()
            logger.info(f"Updated analytics for {user.username}")
            
        except Exception as e:
            logger.error(f"Error updating analytics for {user.username}: {str(e)}")

@shared_task
def check_schedule_conflicts():
    """Check and report schedule conflicts for all users"""
    users = User.objects.all()
    
    for user in users:
        try:
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            for day in days:
                schedules = Schedule.objects.filter(
                    user=user,
                    day=day,
                    is_active=True
                ).order_by('start_time')
                
                # Check for overlaps
                for i in range(len(schedules) - 1):
                    current = schedules[i]
                    next_schedule = schedules[i + 1]
                    
                    if current.end_time > next_schedule.start_time:
                        # Create conflict notification
                        Notification.objects.create(
                            user=user,
                            title='Schedule Conflict Detected',
                            message=f'Conflict on {day}: {current.title} overlaps with {next_schedule.title}',
                            notification_type='system',
                            priority=3,
                            action_url=f'/schedule/{day.lower()}/'
                        )
                        
            logger.info(f"Checked schedule conflicts for {user.username}")
            
        except Exception as e:
            logger.error(f"Error checking conflicts for {user.username}: {str(e)}")

@shared_task
def remind_upcoming_activities():
    """Send reminders for upcoming activities"""
    now = timezone.now()
    reminder_time = now + timedelta(minutes=15)  # 15 minutes from now
    
    # Find activities starting in the next 15 minutes
    upcoming_activities = Schedule.objects.filter(
        start_time__range=(now.time(), reminder_time.time()),
        day=now.strftime('%A'),
        is_active=True,
        notification_sent=False
    ).select_related('user')
    
    for activity in upcoming_activities:
        try:
            # Create reminder notification
            Notification.objects.create(
                user=activity.user,
                title=f'Upcoming: {activity.title}',
                message=f'Starts at {activity.start_time.strftime("%H:%M")}',
                notification_type='reminder',
                priority=2,
                related_schedule=activity,
                action_url='/dashboard/'
            )
            
            # Mark as notified
            activity.notification_sent = True
            activity.save()
            
        except Exception as e:
            logger.error(f"Error creating reminder for activity {activity.id}: {str(e)}")

@shared_task
def cleanup_old_data():
    """Clean up old data to maintain performance"""
    # Delete notifications older than 30 days
    old_notifications = Notification.objects.filter(
        created_at__lt=timezone.now() - timedelta(days=30)
    )
    deleted_count, _ = old_notifications.delete()
    logger.info(f"Deleted {deleted_count} old notifications")
    
    # Delete completed tasks older than 90 days
    old_tasks = Task.objects.filter(
        status='completed',
        completed_at__lt=timezone.now() - timedelta(days=90)
    )
    deleted_count, _ = old_tasks.delete()
    logger.info(f"Deleted {deleted_count} old completed tasks")

@shared_task
def backup_user_data(user_id):
    """Backup user data (placeholder for actual backup implementation)"""
    try:
        user = User.objects.get(id=user_id)
        
        # This would be your actual backup logic
        # For now, just log the backup attempt
        logger.info(f"Backup initiated for user: {user.username}")
        
        # Example: Export user data to JSON
        user_data = {
            'user': {
                'username': user.username,
                'email': user.email,
                'date_joined': user.date_joined.isoformat(),
            },
            'schedules_count': Schedule.objects.filter(user=user).count(),
            'tasks_count': Task.objects.filter(user=user).count(),
            'backup_timestamp': timezone.now().isoformat(),
        }
        
        # In a real implementation, you would save this to cloud storage
        # or send it via email to the user
        
        return f"Backup completed for {user.username}"
        
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found for backup")
        return "Backup failed: User not found"