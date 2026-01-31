import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from exams.models import Notification
from django.utils import timezone


def send_notification(recipient, title, message, category='info', related_exam=None):
    """
    Send a real-time notification via WebSocket
    
    Args:
        recipient: User object (recipient)
        title: Notification title
        message: Notification message
        category: Type (info, success, warning, error)
        related_exam: Optional exam object for context
    """
    # Create notification in database
    notification = Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        category=category,
        related_exam=related_exam,
        is_read=False
    )
    
    # Send via WebSocket if available
    channel_layer = get_channel_layer()
    group_name = f'user_{recipient.id}'
    
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'notification_message',
            'notification_id': notification.id,
            'title': title,
            'message': message,
            'category': category,
            'timestamp': timezone.now().isoformat(),
            'is_read': False
        }
    )
    
    return notification


def send_grading_notification(teacher, exam, pending_count):
    """
    Send grading update notification to teacher
    
    Args:
        teacher: Teacher user object
        exam: Exam object
        pending_count: Number of pending subjective answers
    """
    channel_layer = get_channel_layer()
    group_name = f'grading_notifications_{teacher.id}'
    
    message = f"{pending_count} subjective answer(s) waiting to be graded"
    
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'grading_update',
            'exam_id': exam.id,
            'exam_title': exam.title,
            'pending_count': pending_count,
            'message': message
        }
    )


def broadcast_notification(recipient_ids, title, message, category='info'):
    """
    Send notification to multiple users
    
    Args:
        recipient_ids: List of user IDs
        title: Notification title
        message: Notification message
        category: Type (info, success, warning, error)
    """
    from accounts.models import User
    
    channel_layer = get_channel_layer()
    
    for user_id in recipient_ids:
        try:
            recipient = User.objects.get(id=user_id)
            notification = Notification.objects.create(
                recipient=recipient,
                title=title,
                message=message,
                category=category,
                is_read=False
            )
            
            group_name = f'user_{user_id}'
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'notification_message',
                    'notification_id': notification.id,
                    'title': title,
                    'message': message,
                    'category': category,
                    'timestamp': timezone.now().isoformat(),
                    'is_read': False
                }
            )
        except User.DoesNotExist:
            pass
