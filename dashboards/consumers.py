import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from exams.models import Notification


class NotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time notifications"""
    
    async def connect(self):
        """Called when WebSocket connects"""
        if self.scope['user'].is_authenticated:
            self.user_id = self.scope['user'].id
            self.group_name = f'user_{self.user_id}'
            
            # Add to notification group
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        """Called when WebSocket closes"""
        if self.scope['user'].is_authenticated:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Called when WebSocket receives a message"""
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'mark_as_read':
            notification_id = data.get('notification_id')
            await self.mark_notification_read(notification_id)
    
    # Message handlers
    async def notification_message(self, event):
        """Handle notification messages from group"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'id': event['notification_id'],
            'title': event['title'],
            'message': event['message'],
            'category': event['category'],
            'timestamp': event['timestamp'],
            'is_read': event['is_read']
        }))
    
    async def unread_count_update(self, event):
        """Handle unread count updates"""
        unread_count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'type': 'unread_count',
            'count': unread_count
        }))
    
    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Mark notification as read"""
        try:
            notification = Notification.objects.get(
                id=notification_id,
                recipient=self.scope['user']
            )
            notification.is_read = True
            notification.save()
        except Notification.DoesNotExist:
            pass
    
    @database_sync_to_async
    def get_unread_count(self):
        """Get count of unread notifications"""
        return Notification.objects.filter(
            recipient=self.scope['user'],
            is_read=False
        ).count()


class GradingNotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for teacher grading notifications"""
    
    async def connect(self):
        """Called when WebSocket connects"""
        if self.scope['user'].is_authenticated and self.scope['user'].role == 'teacher':
            self.user_id = self.scope['user'].id
            self.group_name = f'grading_notifications_{self.user_id}'
            
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        """Called when WebSocket closes"""
        if self.scope['user'].is_authenticated:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
    
    async def grading_update(self, event):
        """Handle grading update messages"""
        await self.send(text_data=json.dumps({
            'type': 'grading_update',
            'exam_id': event['exam_id'],
            'exam_title': event['exam_title'],
            'pending_count': event['pending_count'],
            'message': event['message']
        }))


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for Enterprise Chat.
    Handles real-time messaging for DMs and Rooms.
    """
    async def connect(self):
        if self.scope['user'].is_authenticated:
            self.user = self.scope['user']
            # Join user's personal channel for DMs
            self.user_group = f"chat_user_{self.user.id}"
            await self.channel_layer.group_add(self.user_group, self.channel_name)
            
            # Join all rooms the user is part of (handled dynamically on message, or join all now)
            # Better to join specific room channels when the user "enters" them on frontend?
            # Or just broadcast to 'chat_room_{id}' and let the backend handle who receives it?
            # For simplicity in this architecture:
            # - DMs go to 'chat_user_{id}'
            # - Room messages go to 'chat_room_{id}'
            # User must subscribe to room updates. 
            # For now, we will just rely on the user group for DMs. 
            # For rooms, we might need a separate mechanism or just push to all participants' user groups.
            # Pushing to user groups is safer for permission checks.
            
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if self.scope['user'].is_authenticated:
            await self.channel_layer.group_discard(self.user_group, self.channel_name)
            
            # Leave room groups if we joined any
            # (If we implement room joining logic)

    async def receive(self, text_data):
        """
        Handle incoming WebSocket messages.
        Supported types: 'typing', 'video_offer', 'video_answer', 'new_ice_candidate'
        """
        data = json.loads(text_data)
        msg_type = data.get('type')
        
        if msg_type == 'typing':
            # Broadcast typing status to the recipient
            target_id = data.get('target_id')
            if target_id:
                await self.channel_layer.group_send(
                    f"chat_user_{target_id}",
                    {
                        'type': 'chat_signal',
                        'data': {
                            'type': 'typing',
                            'sender_id': self.user.id,
                            'is_typing': data.get('is_typing', False)
                        }
                    }
                )
        
        elif msg_type in ['video_offer', 'video_answer', 'new_ice_candidate']:
            # Relay WebRTC signaling messages
            target_id = data.get('target_id')
            if target_id:
                await self.channel_layer.group_send(
                    f"chat_user_{target_id}",
                    {
                        'type': 'chat_signal',
                        'data': {
                            'type': msg_type,
                            'sender_id': self.user.id,
                            'payload': data.get('payload')
                        }
                    }
                )

    async def chat_signal(self, event):
        """
        Handler for signaling messages (typing, video calls).
        """
        await self.send(text_data=json.dumps(event['data']))

    async def chat_message(self, event):
        """
        Standard event handler for sending chat data to the WebSocket.
        Expected event structure:
        {
            'type': 'chat_message',
            'data': { ... message payload ... }
        }
        """
        await self.send(text_data=json.dumps(event['data']))
