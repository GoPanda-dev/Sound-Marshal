# core/context_processors.py

from .models import Notification

def unread_notifications(request):
    if request.user.is_authenticated:
        unread_notifications_count = request.user.notifications.filter(is_read=False).count()
        recent_notifications = request.user.notifications.order_by('-created_at')[:5]
    else:
        unread_notifications_count = 0
        recent_notifications = []

    return {
        'unread_notifications_count': unread_notifications_count,
        'recent_notifications': recent_notifications,
    }
