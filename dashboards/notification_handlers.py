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
        category: Type (info, success, warning, error) - Ignored for exams.models.Notification
        related_exam: Optional exam object for context
    """
    # Create notification in database
    # Using exams.models.Notification which has sender, recipient, title, message, is_read, related_exam (int)
    # It does not have category
    
    related_exam_id = related_exam.id if related_exam and hasattr(related_exam, 'id') else related_exam
    
    # We need a sender. exams.models.Notification requires a sender.
    # But this handler doesn't take a sender.
    # We might need to make sender optional in the model or provide a default system user.
    # For now, let's see if we can get away with it or if we need to modify the model.
    # The model definition: sender = models.ForeignKey(..., on_delete=models.CASCADE)
    # It is NOT NULL.
    
    # We need to fetch a system user or admin to be the sender.
    from accounts.models import User
    sender = User.objects.filter(is_superuser=True).first()
    if not sender:
        # Fallback if no admin exists (unlikely in prod but possible in test)
        sender = recipient # Self-notification as fallback?
        
    notification = Notification.objects.create(
        sender=sender,
        recipient=recipient,
        title=title,
        message=message,
        related_exam=related_exam_id,
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
        category: Type (info, success, warning, error) - Ignored
    """
    from accounts.models import User
    
    channel_layer = get_channel_layer()
    
    # Get default sender
    sender = User.objects.filter(is_superuser=True).first()
    
    for user_id in recipient_ids:
        try:
            recipient = User.objects.get(id=user_id)
            # Use sender if available, else fallback to recipient (self-notification)
            # This is a fallback for the schema requirement
            msg_sender = sender if sender else recipient
            
            notification = Notification.objects.create(
                sender=msg_sender,
                recipient=recipient,
                title=title,
                message=message,
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
