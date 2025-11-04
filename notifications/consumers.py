# notifications/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # همه کاربران به یک گروه اضافه میشن
        self.group_name = f"user_{self.scope['user'].id}" if self.scope['user'].is_authenticated else "anonymous"      
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        # اتصال WebSocket قبول میشه
        await self.accept()

        # پیام خوش‌آمدگویی
        await self.send(text_data=json.dumps({
            "type": "welcome",
            "message": f"Hello {self.scope['user'].username if self.scope['user'].is_authenticated else 'Guest'}, WebSocket connected!"
        }))

    async def disconnect(self, close_code):
        # هنگام قطع اتصال از گروه خارج میشه
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_notification(self, event):
        await self.send(text_data=json.dumps(event["content"]))
