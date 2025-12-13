import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.utils import timezone
from pickup.models import PickupCode 
import uuid # Needed for UUID field check


# --- 1. Exam Monitoring Consumer ---pip
class ExamMonitorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # The session ID is passed in the URL (e.g., ws/exam/123/)
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f'exam_{self.session_id}'

        # Join room group (The student's browser joins this group)
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Accept the connection
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket (Heartbeat from the student)
    async def receive(self, text_data):
        """
        Handles incoming heartbeats or status updates from the student's browser.
        """
        text_data_json = json.loads(text_data)
        status = text_data_json.get('status')
        # Here, you would update the CBTExamSession model 
        # (e.g., using sync_to_async) to record the latest heartbeat time.
        
        print(f"Exam Session {self.session_id}: Received status: {status}")

    # Receive message from room group (e.g., Admin forcing an end to the exam)
    async def exam_status_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'status_update',
            'message': message
        }))



# --- 2. Communication Consumer (Broadcast/Chat) ---
class CommunicationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        
        # Define two groups: 
        self.staff_group = 'staff_chat'          # For bi-directional chat
        self.student_group = 'student_broadcast' # For uni-directional announcements
        
        # User Authentication Check
        if not user.is_authenticated:
            await self.close()
            return

        # Determine user role and assign to groups
        if user.role in ['ADMIN', 'STAFF']: # Assuming we define Staff/Teacher roles later
            # Staff/Admin/Teacher joins the bi-directional group
            await self.channel_layer.group_add(self.staff_group, self.channel_name)
        
        if user.role == 'STUDENT':
            # Student joins the receive-only broadcast group
            await self.channel_layer.group_add(self.student_group, self.channel_name)
        
        await self.accept()

    async def disconnect(self, close_code):
        user = self.scope["user"]
        if user.role in ['ADMIN', 'STAFF']:
            await self.channel_layer.group_discard(self.staff_group, self.channel_name)
        if user.role == 'STUDENT':
            await self.channel_layer.group_discard(self.student_group, self.channel_name)

    async def receive(self, text_data):
        """
        Handles incoming messages from the client.
        Students cannot send, so we only process messages from Staff/Admin.
        """
        user = self.scope["user"]
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        message_type = text_data_json.get('type', 'chat') # 'chat' or 'broadcast'

        # Only process messages from Staff/Admin
        if user.role in ['ADMIN', 'STAFF']:
            
            if message_type == 'chat':
                # Send to the Staff/Admin group (Bi-directional chat)
                await self.channel_layer.group_send(
                    self.staff_group,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'sender': user.username
                    }
                )
            
            elif message_type == 'broadcast':
                # Send to the Student group (Uni-directional announcement)
                await self.channel_layer.group_send(
                    self.student_group,
                    {
                        'type': 'broadcast_message',
                        'message': message,
                        'sender': user.username
                    }
                )

    # Receive message from 'staff_chat' group
    async def chat_message(self, event):
        # Staff/Admin receive this. Students DO NOT join this group.
        await self.send(text_data=json.dumps({
            'type': 'chat',
            'sender': event['sender'],
            'message': event['message']
        }))

    # Receive message from 'student_broadcast' group
    async def broadcast_message(self, event):
        # Staff/Admin/Student receive this (since both are added for receiving broadcasts)
        await self.send(text_data=json.dumps({
            'type': 'broadcast',
            'sender': event['sender'],
            'message': event['message']
        }))



# --- 3. PTA Private Chat Consumer ---
class PTAChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'pta_{self.room_name}'
        
        # User authentication and authorization check should happen here
        # E.g., check if the connecting user is one of the two allowed users in the room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.scope['user'].username
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat',
            'sender': sender,
            'message': message
        }))



# --- 4. Pickup Verification Consumer ---
class PickupCodeConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        # Staff/Admin users only connect to the verification terminal
        if self.scope["user"].is_authenticated and self.scope["user"].role in ['ADMIN', 'STAFF']:
            await self.accept()
            # Group for sending verification status updates
            await self.channel_layer.group_add(
                "verification_terminal",
                self.channel_name
            )
        else:
            await self.close()

    async def disconnect(self, close_code):
        if self.scope["user"].is_authenticated:
            await self.channel_layer.group_discard(
                "verification_terminal",
                self.channel_name
            )

    async def receive(self, text_data):
        """Receives the code (UUID string) from the Staff verification terminal."""
        data = json.loads(text_data)
        code_str = data.get('code')
        
        # Validation and Verification must be done synchronously
        result = await sync_to_async(self.validate_and_verify)(code_str, self.scope["user"])

        # Send result back to the specific channel
        await self.send(text_data=json.dumps(result))
        
        # Also broadcast successful verification to all terminals
        if result['status'] == 'success':
            await self.channel_layer.group_send(
                "verification_terminal",
                {
                    'type': 'verification_update',
                    'message': result
                }
            )

    def validate_and_verify(self, code_str, staff_user):
        """Performs the synchronous lookup and update."""
        
        try:
            # 1. Attempt to find the code (UUID conversion)
            code_uuid = uuid.UUID(code_str)
            code_instance = PickupCode.objects.get(code=code_uuid)
            
            # 2. Check Expiry
            if code_instance.is_expired():
                return {
                    'status': 'error',
                    'message': "Code is expired.",
                    'details': f"Code was valid until: {code_instance.expires_at.strftime('%Y-%m-%d %H:%M')}"
                }
            
            # 3. Check if Already Used
            if code_instance.is_verified:
                return {
                    'status': 'error',
                    'message': "Code already used.",
                    'details': f"Verified by {code_instance.verified_by.get_full_name()} at {code_instance.verified_by}"
                }
                
            # 4. Success: Mark as verified and save staff user
            code_instance.is_verified = True
            code_instance.verified_by = staff_user
            code_instance.save()
            
            return {
                'status': 'success',
                'message': f"Verification successful for {code_instance.student.get_full_name()}!",
                'student_name': code_instance.student.get_full_name(),
                'parent_name': code_instance.parent.get_full_name(),
                'verified_by': staff_user.get_full_name(),
                'time': timezone.now().strftime("%H:%M:%S")
            }

        except ValueError:
            return {'status': 'error', 'message': "Invalid code format (must be a UUID)."}
        except PickupCode.DoesNotExist:
            return {'status': 'error', 'message': "Code not found."}
        except Exception as e:
            return {'status': 'error', 'message': f"An unexpected error occurred: {e}"}

    # Handler for group_send broadcasts
    async def verification_update(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))