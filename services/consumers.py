import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            return

        self.group_name = f'user_notifications_{user.id}'
        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)

    def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)

    def send_notification(self, event):
        payload = event.get('payload', {})
        self.send(text_data=json.dumps(payload))
