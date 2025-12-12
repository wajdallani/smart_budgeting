from .models import Notification

def notifications_context(request):
    if request.user.is_authenticated:
        qs = Notification.objects.filter(user=request.user).order_by('-created_at')
        return {
            "unread_notifications_count": qs.filter(is_read=False).count(),
            "navbar_notifications": qs[:3],  # last 3 notifications
        }
    return {
        "unread_notifications_count": 0,
        "navbar_notifications": [],
    }
