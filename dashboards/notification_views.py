from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from exams.models import Notification
import json


@login_required()
@require_http_methods(["GET"])
def notifications_list(request):
    """List all notifications for the user"""
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(notifications, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'notifications': page_obj,
        'unread_count': Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count(),
    }
    
    return render(request, 'notifications/list.html', context)


@login_required()
@require_http_methods(["GET"])
def get_unread_notifications(request):
    """API endpoint to get unread notifications (AJAX)"""
    notifications = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).order_by('-created_at')[:5]
    
    data = {
        'count': Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count(),
        'notifications': [
            {
                'id': n.id,
                'title': n.title,
                'message': n.message,
                # 'category': n.category,
                'is_read': n.is_read
            }
            for n in notifications
        ]
    }
    
    return JsonResponse(data)


@login_required()
@require_http_methods(["POST"])
def mark_as_read(request):
    """Mark a notification as read"""
    try:
        data = json.loads(request.body)
        notification_id = data.get('notification_id')
        
        notification = Notification.objects.get(
            id=notification_id,
            recipient=request.user
        )
        notification.is_read = True
        notification.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Notification marked as read',
            'unread_count': Notification.objects.filter(
                recipient=request.user,
                is_read=False
            ).count()
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required()
@require_http_methods(["POST"])
def mark_all_as_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(is_read=True)
    
    return JsonResponse({
        'success': True,
        'message': 'All notifications marked as read',
        'unread_count': 0
    })


@login_required()
@require_http_methods(["DELETE"])
def delete_notification(request, notification_id):
    """Delete a notification"""
    try:
        notification = Notification.objects.get(
            id=notification_id,
            recipient=request.user
        )
        notification.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Notification deleted'
        })
    except Notification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Notification not found'
        }, status=404)


@login_required()
@require_http_methods(["GET"])
def notification_detail(request, notification_id):
    """Get detail of a specific notification"""
    try:
        notification = Notification.objects.get(
            id=notification_id,
            recipient=request.user
        )
        
        # Mark as read
        if not notification.is_read:
            notification.is_read = True
            notification.save()
        
        context = {
            'notification': notification,
        }
        
        return render(request, 'notifications/detail.html', context)
    except Notification.DoesNotExist:
        return render(request, 'notifications/not_found.html', status=404)
