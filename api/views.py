from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.db.models import Q
from core.models import (
    UserProfile, Schedule, JKUATTimetable, Task, ProgressTracker,
    Habit, HabitCompletion, Achievement, UserAchievement,
    ResourceCategory, ActivityResource, UserResourcePreference,
    Team, TeamMembership, SmartSuggestion, ChatRoom, ChatMessage,
    AnalyticsDashboard
)
from notifications.models import Notification, NotificationPreference
from .serializers import *
import logging

logger = logging.getLogger(__name__)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Get current user's profile"""
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    @action(detail=False, methods=['put'])
    def update_profile(self, request):
        """Update current user's profile"""
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TeamViewSet(viewsets.ModelViewSet):
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Team.objects.filter(members=self.request.user, is_active=True)

    @action(detail=True, methods=['post'])
    def invite_member(self, request, pk=None):
        """Invite member to team"""
        team = self.get_object()
        serializer = TeamInviteSerializer(data=request.data)
        
        if serializer.is_valid():
            # Check permissions
            membership = TeamMembership.objects.get(team=team, user=request.user)
            if membership.role not in ['owner', 'admin']:
                return Response(
                    {'error': 'Insufficient permissions'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # TODO: Send invitation email
            return Response({'message': 'Invitation sent successfully'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get team members"""
        team = self.get_object()
        memberships = TeamMembership.objects.filter(team=team)
        serializer = TeamMembershipSerializer(memberships, many=True)
        return Response(serializer.data)

class ScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Schedule.objects.filter(
            Q(user=user) | Q(team__members=user) | Q(shared_with=user),
            is_active=True
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def day_schedule(self, request):
        """Get schedule for specific day"""
        day = request.query_params.get('day', '')
        if not day:
            return Response({'error': 'Day parameter required'}, status=400)
        
        schedules = self.get_queryset().filter(day=day).order_by('start_time')
        serializer = self.get_serializer(schedules, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def check_conflict(self, request):
        """Check for schedule conflicts"""
        serializer = ScheduleConflictSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            
            conflicts = Schedule.objects.filter(
                user_id=data['user_id'],
                day=data['day'],
                start_time__lt=data['end_time'],
                end_time__gt=data['start_time'],
                is_active=True
            )
            
            if 'schedule_id' in data:
                conflicts = conflicts.exclude(pk=data['schedule_id'])
            
            has_conflict = conflicts.exists()
            return Response({'has_conflict': has_conflict, 'conflicts': conflicts.count()})
        
        return Response(serializer.errors, status=400)

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(
            Q(user=user) | Q(team__members=user) | Q(assigned_to=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign task to users"""
        task = self.get_object()
        user_ids = request.data.get('user_ids', [])
        
        users = User.objects.filter(id__in=user_ids)
        task.assigned_to.set(users)
        task.save()
        
        return Response({'message': 'Task assigned successfully'})

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark task as completed"""
        task = self.get_object()
        task.status = 'completed'
        task.completed_at = timezone.now()
        task.save()
        
        return Response({'message': 'Task completed successfully'})

class SmartSuggestionViewSet(viewsets.ModelViewSet):
    serializer_class = SmartSuggestionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SmartSuggestion.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        """Apply a smart suggestion"""
        suggestion = self.get_object()
        suggestion.is_applied = True
        suggestion.save()
        
        # TODO: Implement specific application logic based on suggestion type
        return Response({'message': 'Suggestion applied successfully'})

class ChatRoomViewSet(viewsets.ModelViewSet):
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatRoom.objects.filter(participants=self.request.user, is_active=True)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get messages for a chat room"""
        room = self.get_object()
        messages = ChatMessage.objects.filter(room=room).order_by('created_at')
        serializer = ChatMessageSerializer(messages, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send message to chat room"""
        room = self.get_object()
        content = request.data.get('content', '').strip()
        
        if not content:
            return Response({'error': 'Message content required'}, status=400)
        
        message = ChatMessage.objects.create(
            room=room,
            sender=request.user,
            content=content
        )
        
        serializer = ChatMessageSerializer(message, context={'request': request})
        return Response(serializer.data)

class AnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def productivity_stats(self, request):
        """Get productivity statistics"""
        days = int(request.query_params.get('days', 30))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        progress_data = ProgressTracker.objects.filter(
            user=request.user,
            date__range=[start_date, end_date]
        ).order_by('date')
        
        stats = {
            'total_study_hours': progress_data.aggregate(Sum('study_hours'))['study_hours__sum'] or 0,
            'avg_productivity': progress_data.aggregate(Avg('productivity_score'))['productivity_score__avg'] or 0,
            'total_tasks_completed': progress_data.aggregate(Sum('tasks_completed'))['tasks_completed__sum'] or 0,
            'workout_days': progress_data.filter(workout_completed=True).count(),
        }
        
        return Response(stats)

    @action(detail=False, methods=['get'])
    def weekly_report(self, request):
        """Get weekly productivity report"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=6)
        
        weekly_data = []
        for i in range(7):
            date = start_date + timedelta(days=i)
            progress = ProgressTracker.objects.filter(user=request.user, date=date).first()
            
            weekly_data.append({
                'date': date,
                'productivity_score': progress.productivity_score if progress else 0,
                'study_hours': progress.study_hours if progress else 0,
                'tasks_completed': progress.tasks_completed if progress else 0,
            })
        
        return Response(weekly_data)

class NaturalLanguageViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def parse_schedule(self, request):
        """Parse natural language and create schedule"""
        serializer = NaturalLanguageInputSerializer(data=request.data)
        if serializer.is_valid():
            text = serializer.validated_data['text']
            
            # Simple NLP processing
            # In a real implementation, you'd use spaCy, NLTK, or similar
            words = text.lower().split()
            
            # Extract basic information
            activity_type = 'other'
            preferred_time = 'any'
            
            time_keywords = {'morning', 'afternoon', 'evening', 'night'}
            activity_keywords = {
                'study': 'study', 'workout': 'workout', 'class': 'lecture',
                'meeting': 'meeting', 'project': 'project', 'girlfriend': 'relationship'
            }
            
            for word in words:
                if word in time_keywords:
                    preferred_time = word
                if word in activity_keywords:
                    activity_type = activity_keywords[word]
            
            # Create schedule
            schedule = Schedule.objects.create(
                user=request.user,
                title=text,
                day='Monday',  # Default - enhance with better date parsing
                start_time=time(9, 0),
                end_time=time(10, 0),
                activity_type=activity_type,
                is_flexible=True,
                preferred_time=preferred_time,
                description=f"Created from: {text}",
                ai_generated=True
            )
            
            return Response({
                'message': 'Schedule created successfully',
                'schedule_id': str(schedule.id),
                'activity_type': activity_type,
                'preferred_time': preferred_time
            })
        
        return Response(serializer.errors, status=400)

# Additional ViewSets for other models
class JKUATTimetableViewSet(viewsets.ModelViewSet):
    serializer_class = JKUATTimetableSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return JKUATTimetable.objects.filter(user=self.request.user)

class ProgressTrackerViewSet(viewsets.ModelViewSet):
    serializer_class = ProgressTrackerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ProgressTracker.objects.filter(user=self.request.user)

class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)

class ActivityResourceViewSet(viewsets.ModelViewSet):
    serializer_class = ActivityResourceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ActivityResource.objects.filter(is_active=True)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        """Toggle favorite status for resource"""
        resource = self.get_object()
        preference, created = UserResourcePreference.objects.get_or_create(
            user=request.user,
            resource=resource
        )
        preference.is_favorite = not preference.is_favorite
        preference.save()
        
        return Response({'is_favorite': preference.is_favorite})

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get unread notification count"""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'message': 'Notification marked as read'})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({'message': 'All notifications marked as read'})