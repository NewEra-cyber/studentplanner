from rest_framework import serializers
from django.contrib.auth.models import User
from core.models import (
    UserProfile, Schedule, JKUATTimetable, Task, ProgressTracker, 
    Habit, HabitCompletion, Achievement, UserAchievement,
    ResourceCategory, ActivityResource, UserResourcePreference,
    Team, TeamMembership, SmartSuggestion, ChatRoom, ChatMessage,
    AnalyticsDashboard
)
from notifications.models import Notification, NotificationPreference

class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']
    
    def get_profile(self, obj):
        try:
            profile = obj.profile
            return UserProfileSerializer(profile).data
        except UserProfile.DoesNotExist:
            return None

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = UserProfile
        fields = '__all__'

class TeamSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    created_by_name = serializers.ReadOnlyField(source='created_by.username')
    
    class Meta:
        model = Team
        fields = '__all__'
    
    def get_member_count(self, obj):
        return obj.members.count()

class TeamMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    team_name = serializers.ReadOnlyField(source='team.name')
    
    class Meta:
        model = TeamMembership
        fields = '__all__'

class ScheduleSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    team_name = serializers.ReadOnlyField(source='team.name')
    duration_minutes = serializers.ReadOnlyField()
    is_current = serializers.ReadOnlyField()
    has_conflict = serializers.ReadOnlyField()
    
    class Meta:
        model = Schedule
        fields = '__all__'

class JKUATTimetableSerializer(serializers.ModelSerializer):
    title = serializers.ReadOnlyField()
    
    class Meta:
        model = JKUATTimetable
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    is_overdue = serializers.ReadOnlyField()
    assigned_to_users = UserSerializer(many=True, read_only=True, source='assigned_to')
    team_name = serializers.ReadOnlyField(source='team.name')
    
    class Meta:
        model = Task
        fields = '__all__'

class ProgressTrackerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ProgressTracker
        fields = '__all__'

class HabitSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    current_streak_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Habit
        fields = '__all__'
    
    def get_current_streak_percentage(self, obj):
        if obj.target_count > 0:
            return min(100, (obj.current_streak / obj.target_count) * 100)
        return 0

class HabitCompletionSerializer(serializers.ModelSerializer):
    habit_name = serializers.ReadOnlyField(source='habit.name')
    
    class Meta:
        model = HabitCompletion
        fields = '__all__'

class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = '__all__'

class UserAchievementSerializer(serializers.ModelSerializer):
    achievement = AchievementSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserAchievement
        fields = '__all__'

class ResourceCategorySerializer(serializers.ModelSerializer):
    resource_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ResourceCategory
        fields = '__all__'
    
    def get_resource_count(self, obj):
        return obj.resources.filter(is_active=True).count()

class ActivityResourceSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    is_favorite = serializers.SerializerMethodField()
    user_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = ActivityResource
        fields = '__all__'
    
    def get_is_favorite(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            try:
                preference = UserResourcePreference.objects.get(user=user, resource=obj)
                return preference.is_favorite
            except UserResourcePreference.DoesNotExist:
                return False
        return False
    
    def get_user_rating(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            try:
                preference = UserResourcePreference.objects.get(user=user, resource=obj)
                return preference.user_rating
            except UserResourcePreference.DoesNotExist:
                return None
        return None

class UserResourcePreferenceSerializer(serializers.ModelSerializer):
    resource = ActivityResourceSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserResourcePreference
        fields = '__all__'

class SmartSuggestionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = SmartSuggestion
        fields = '__all__'

class ChatRoomSerializer(serializers.ModelSerializer):
    participant_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    created_by_name = serializers.ReadOnlyField(source='created_by.username')
    
    class Meta:
        model = ChatRoom
        fields = '__all__'
    
    def get_participant_count(self, obj):
        return obj.participants.count()
    
    def get_last_message(self, obj):
        last_message = obj.messages.last()
        if last_message:
            return {
                'content': last_message.content[:100],
                'sender': last_message.sender.username,
                'timestamp': last_message.created_at
            }
        return None

class ChatMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    room_name = serializers.ReadOnlyField(source='room.name')
    is_own_message = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatMessage
        fields = '__all__'
    
    def get_is_own_message(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.sender == request.user
        return False

class AnalyticsDashboardSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = AnalyticsDashboard
        fields = '__all__'

# Notification Serializers
class NotificationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Notification
        fields = '__all__'

class NotificationPreferenceSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = NotificationPreference
        fields = '__all__'

# AI/NLP Serializers
class NaturalLanguageInputSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=500)
    
    def validate_text(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Input text is too short")
        return value

class ScheduleConflictSerializer(serializers.Serializer):
    schedule_id = serializers.UUIDField(required=False)
    day = serializers.CharField(max_length=10)
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    user_id = serializers.IntegerField()

class ProductivityAnalyticsSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    metrics = serializers.ListField(
        child=serializers.ChoiceField(choices=[
            'study_time', 'workout_time', 'tasks_completed', 
            'productivity_score', 'sleep_quality'
        ])
    )

# File Management Serializers
class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    folder = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)

class FolderCreateSerializer(serializers.Serializer):
    folder_name = serializers.CharField(max_length=100)
    parent_folder = serializers.CharField(required=False, allow_blank=True)

class FileContentSerializer(serializers.Serializer):
    filename = serializers.CharField()
    folder = serializers.CharField(required=False, allow_blank=True)
    content = serializers.CharField(required=False, allow_blank=True)

# Team Collaboration Serializers
class TeamInviteSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=TeamMembership.ROLE_CHOICES)

class TeamActivitySerializer(serializers.Serializer):
    team_id = serializers.UUIDField()
    activity_type = serializers.ChoiceField(choices=[
        'schedule_created', 'task_completed', 'resource_shared', 
        'message_sent', 'meeting_scheduled'
    ])
    description = serializers.CharField()

# Weather Serializer
class WeatherSerializer(serializers.Serializer):
    temperature = serializers.IntegerField()
    description = serializers.CharField()
    humidity = serializers.IntegerField()
    wind_speed = serializers.FloatField()
    icon = serializers.CharField()
    feels_like = serializers.IntegerField()
    background_class = serializers.CharField()