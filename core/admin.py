from django.contrib import admin
from .models import UserProfile, Schedule, Task, ProgressTracker, JKUATTimetable, ResourceCategory, ActivityResource, UserResourcePreference

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'wake_up_time', 'sleep_time', 'current_phase', 'streak_count', 'total_points']
    list_filter = ['current_phase', 'theme']
    search_fields = ['user__username', 'course']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['user', 'day', 'start_time', 'end_time', 'title', 'activity_type', 'is_active']
    list_filter = ['day', 'activity_type', 'user', 'is_active']
    search_fields = ['title', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'id']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'priority', 'status', 'due_date']
    list_filter = ['status', 'priority', 'user']
    search_fields = ['title', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'id']

@admin.register(ProgressTracker)
class ProgressTrackerAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'tasks_completed', 'productivity_score']
    list_filter = ['user', 'date']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'id']

@admin.register(JKUATTimetable)
class JKUATTimetableAdmin(admin.ModelAdmin):
    list_display = ['user', 'day', 'start_time', 'end_time', 'course_code', 'venue', 'is_active']
    list_filter = ['day', 'user', 'is_active']
    search_fields = ['course_code', 'course_name', 'venue']

@admin.register(ResourceCategory)
class ResourceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']
    readonly_fields = ['created_at', 'id']

@admin.register(ActivityResource)
class ActivityResourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'resource_type', 'activity_type', 'is_free', 'is_active']
    list_filter = ['category', 'resource_type', 'is_free', 'is_active']
    search_fields = ['name', 'category__name']
    readonly_fields = ['created_at', 'updated_at', 'id']

@admin.register(UserResourcePreference)
class UserResourcePreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'resource', 'is_favorite', 'created_at']
    list_filter = ['is_favorite', 'user']
    search_fields = ['user__username', 'resource__name']
    readonly_fields = ['created_at', 'updated_at', 'id']