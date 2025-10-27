from django.contrib import admin
from .models import Notification, NotificationPreference

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'push_enabled', 'email_enabled', 'quiet_hours_enabled']
    list_filter = ['push_enabled', 'email_enabled']
    search_fields = ['user__username']