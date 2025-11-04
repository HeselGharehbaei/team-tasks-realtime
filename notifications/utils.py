from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification

def send_realtime_notification(user, type_, title, message, task=None):
    """هم ذخیره در DB و هم ارسال WebSocket"""
    # ذخیره در دیتابیس
    notif = Notification.objects.create(
        user=user,
        type=type_,
        title=title,
        message=message,
        task=task
    )

    # ارسال بلادرنگ
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "all_users",
        {
            "type": "send_notification",
            "content": {
                "type": type_,
                "title": title,
                "message": message,
            }
        }
    )

    return notif
