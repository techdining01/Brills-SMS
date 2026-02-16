from django.conf import settings
from exams.models import Notification, ChatMessage

def school_context(request):
    context = {
        'SCHOOL_NAME': settings.SCHOOL_NAME,
        'SCHOOL_SLOGAN': settings.SCHOOL_SLOGAN,
        'PORTAL_DOMAIN': settings.PORTAL_DOMAIN
    }
    
    if request.user.is_authenticated:
        # Get unread notifications count
        unread_notifications = Notification.objects.filter(
            recipient=request.user, 
            is_read=False
        ).count()
        
        # Get unread chat messages count
        unread_chats = ChatMessage.objects.filter(
            recipient=request.user, 
            is_read=False
        ).count()
        
        # Get recent notifications (limit 5)
        recent_notifications = list(Notification.objects.filter(
            recipient=request.user
        ).order_by('-created_at')[:5])

        # Get recent chat messages (limit 5)
        recent_chats = list(ChatMessage.objects.filter(
            recipient=request.user,
            is_read=False
        ).order_by('-created_at')[:5])

        context.update({
            'unread_notifications_count': unread_notifications,
            'unread_chats_count': unread_chats,
            'total_unread_count': unread_notifications + unread_chats,
            'recent_notifications': recent_notifications,
            'recent_chats': recent_chats
        })
        
    return context