import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from core.models import ChatRoom, ChatMessage

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        self.room_group_name = f'notifications_{self.user.id}'
        
        # Join notification group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial unread count
        unread_count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'type': 'initial_count',
            'unread_count': unread_count
        }))

    async def disconnect(self, close_code):
        # Leave notification group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'mark_read':
            notification_id = text_data_json.get('notification_id')
            await self.mark_notification_read(notification_id)
            
            # Send updated count
            unread_count = await self.get_unread_count()
            await self.send(text_data=json.dumps({
                'type': 'unread_count',
                'unread_count': unread_count
            }))

    async def notification_message(self, event):
        """Receive notification from group"""
        notification = event['notification']
        
        # Send notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'new_notification',
            'notification': notification
        }))
        
        # Send updated count
        unread_count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'type': 'unread_count',
            'unread_count': unread_count
        }))

    @database_sync_to_async
    def get_unread_count(self):
        from .models import Notification
        return Notification.objects.filter(user=self.user, is_read=False).count()

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        from .models import Notification
        try:
            notification = Notification.objects.get(id=notification_id, user=self.user)
            notification.is_read = True
            notification.save()
        except Notification.DoesNotExist:
            pass

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close()
            return

        # Check if user is a participant of the room
        if not await self.is_room_participant():
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send room info and recent messages
        room_info = await self.get_room_info()
        await self.send(text_data=json.dumps({
            'type': 'room_info',
            'room': room_info
        }))

        # Send last 50 messages
        recent_messages = await self.get_recent_messages()
        await self.send(text_data=json.dumps({
            'type': 'message_history',
            'messages': recent_messages
        }))

        # Notify others that user joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'user_id': self.user.id,
                'username': self.user.username
            }
        )

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Notify others that user left
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_left',
                    'user_id': self.user.id,
                    'username': self.user.username
                }
            )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')

        if message_type == 'chat_message':
            message_content = text_data_json.get('message', '').strip()
            
            if message_content:
                # Save message to database
                message = await self.save_message(message_content)
                
                # Send message to room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': {
                            'id': str(message.id),
                            'content': message.content,
                            'sender': {
                                'id': message.sender.id,
                                'username': message.sender.username,
                                'first_name': message.sender.first_name,
                                'last_name': message.sender.last_name,
                            },
                            'timestamp': message.created_at.isoformat(),
                            'is_edited': message.is_edited,
                            'is_own_message': False
                        }
                    }
                )

        elif message_type == 'typing':
            # Broadcast typing indicator
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_typing',
                    'user_id': self.user.id,
                    'username': self.user.username,
                    'is_typing': text_data_json.get('is_typing', False)
                }
            )

        elif message_type == 'mark_read':
            message_id = text_data_json.get('message_id')
            await self.mark_message_read(message_id)

    async def chat_message(self, event):
        """Receive chat message from room group"""
        message = event['message']
        
        # Mark as own message if sent by current user
        message['is_own_message'] = message['sender']['id'] == self.user.id
        
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message
        }))

    async def user_joined(self, event):
        """Handle user joined event"""
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'user_id': event['user_id'],
            'username': event['username'],
            'timestamp': await self.get_current_timestamp()
        }))

    async def user_left(self, event):
        """Handle user left event"""
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'user_id': event['user_id'],
            'username': event['username'],
            'timestamp': await self.get_current_timestamp()
        }))

    async def user_typing(self, event):
        """Handle typing indicator"""
        if event['user_id'] != self.user.id:  # Don't send own typing indicator to self
            await self.send(text_data=json.dumps({
                'type': 'user_typing',
                'user_id': event['user_id'],
                'username': event['username'],
                'is_typing': event['is_typing']
            }))

    @database_sync_to_async
    def is_room_participant(self):
        try:
            room = ChatRoom.objects.get(id=self.room_id, participants=self.user)
            return True
        except ChatRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def get_room_info(self):
        room = ChatRoom.objects.get(id=self.room_id)
        return {
            'id': str(room.id),
            'name': room.name,
            'description': room.description,
            'room_type': room.room_type,
            'participant_count': room.participants.count(),
            'created_by': room.created_by.username
        }

    @database_sync_to_async
    def get_recent_messages(self):
        messages = ChatMessage.objects.filter(room_id=self.room_id).select_related('sender').order_by('created_at')[:50]
        
        message_list = []
        for message in messages:
            message_list.append({
                'id': str(message.id),
                'content': message.content,
                'sender': {
                    'id': message.sender.id,
                    'username': message.sender.username,
                    'first_name': message.sender.first_name,
                    'last_name': message.sender.last_name,
                },
                'timestamp': message.created_at.isoformat(),
                'is_edited': message.is_edited,
                'is_own_message': message.sender == self.user
            })
        
        return message_list

    @database_sync_to_async
    def save_message(self, content):
        room = ChatRoom.objects.get(id=self.room_id)
        message = ChatMessage.objects.create(
            room=room,
            sender=self.user,
            content=content
        )
        return message

    @database_sync_to_async
    def mark_message_read(self, message_id):
        try:
            message = ChatMessage.objects.get(id=message_id)
            message.read_by.add(self.user)
        except ChatMessage.DoesNotExist:
            pass

    @sync_to_async
    def get_current_timestamp(self):
        from django.utils import timezone
        return timezone.now().isoformat()

class AnalyticsConsumer(AsyncWebsocketConsumer):
    """Real-time analytics updates"""
    async def connect(self):
        self.user = self.scope["user"]
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        self.analytics_group_name = f'analytics_{self.user.id}'
        
        # Join analytics group
        await self.channel_layer.group_add(
            self.analytics_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial analytics data
        analytics_data = await self.get_initial_analytics()
        await self.send(text_data=json.dumps({
            'type': 'initial_analytics',
            'data': analytics_data
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.analytics_group_name,
            self.channel_name
        )

    async def analytics_update(self, event):
        """Receive analytics update"""
        await self.send(text_data=json.dumps({
            'type': 'analytics_update',
            'data': event['data']
        }))

    @database_sync_to_async
    def get_initial_analytics(self):
        from core.models import ProgressTracker, Task
        from django.utils import timezone
        from datetime import timedelta
        
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        # Get weekly stats
        weekly_progress = ProgressTracker.objects.filter(
            user=self.user,
            date__range=[week_ago, today]
        )
        
        total_study = weekly_progress.aggregate(Sum('study_hours'))['study_hours__sum'] or 0
        avg_productivity = weekly_progress.aggregate(Avg('productivity_score'))['productivity_score__avg'] or 0
        tasks_completed = Task.objects.filter(
            user=self.user,
            status='completed',
            completed_at__date__range=[week_ago, today]
        ).count()
        
        return {
            'weekly_study_hours': round(total_study, 1),
            'weekly_productivity': round(avg_productivity, 1),
            'weekly_tasks_completed': tasks_completed,
            'current_streak': self.user.profile.streak_count
        }