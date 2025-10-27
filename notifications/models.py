from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('reminder', '🔔 Reminder'),
        ('achievement', '🏆 Achievement'),
        ('system', '⚙️ System'),
        ('team', '👥 Team'),
        ('schedule', '📅 Schedule'),
        ('task', '✅ Task'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='system')
    is_read = models.BooleanField(default=False)
    related_model = models.CharField(max_length=50, blank=True)
    related_id = models.UUIDField(null=True, blank=True)
    action_url = models.URLField(blank=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['user', 'notification_type']),
            models.Index(fields=['scheduled_for']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"

class NotificationPreference(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Push notification preferences
    push_enabled = models.BooleanField(default=True)
    push_reminders = models.BooleanField(default=True)
    push_achievements = models.BooleanField(default=True)
    push_team_updates = models.BooleanField(default=True)
    push_schedule_changes = models.BooleanField(default=True)
    
    # Email notification preferences
    email_enabled = models.BooleanField(default=False)
    email_digest = models.BooleanField(default=True)
    email_reminders = models.BooleanField(default=False)
    email_achievements = models.BooleanField(default=True)
    email_team_updates = models.BooleanField(default=False)
    
    # Scheduling preferences
    quiet_hours_start = models.TimeField(default='22:00:00')
    quiet_hours_end = models.TimeField(default='06:00:00')
    quiet_hours_enabled = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_preferences'
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'
    
    def __str__(self):
        return f"{self.user.username}'s Notification Preferences"