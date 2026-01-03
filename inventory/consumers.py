import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("DEBUG: Client connected to WebSocket!")
        await self.channel_layer.group_add("inventory_alerts", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("inventory_alerts", self.channel_name)

    # YE WALA FUNCTION CHECK KARO - Iska naam 'send_notification' hi hona chahiye
    async def send_notification(self, event):
        # Ye line terminal mein dikhni chahiye jab script chalao
        print(f"DEBUG: Consumer received message: {event['message']}") 
        
        message = event['message']
        await self.send(text_data=json.dumps({
            'alert': message
        }))