import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # هر کسی که وصل میشه، عضو گروه "all_users" میشه
        self.group_name = "all_users"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        # قبول اتصال WebSocket
        await self.accept()
        # پیام خوش‌آمدگویی به کاربر وصل شده
        await self.send(text_data=json.dumps({
            "message": "WebSocket connected!"
        }))

    async def disconnect(self, close_code):
        # وقتی اتصال قطع شد، از گروه "all_users" خارج میشه
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_notification(self, event):
        # دریافت پیام از کانال لایه و ارسال به WebSocket
        await self.send(text_data=json.dumps(event["content"]))
