from .models import Notification

def notifications_processor(request):
    """
    Context processor to make notifications and unread count available globally
    """
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        unread_count = notifications.count()
        return {
            'notifications': notifications,
            'unread_count': unread_count
        }
    return {
        'notifications': [],
        'unread_count': 0
    } 