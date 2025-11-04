from django.urls import re_path
from .consumers import NotificationConsumer

def get_websocket_urlpatterns():
    return [
        re_path(r'ws/notifications/$', NotificationConsumer.as_asgi()),
    ]