import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from chat.presence import mark_user_offline, mark_user_online


class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            self.close()
            return

        self.accept()

        self.user_id = user.id

        self.group_name = f'user_notifications_{user.id}'
        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
        mark_user_online(self.user_id, self.channel_name)

    def disconnect(self, close_code):
        if hasattr(self, 'user_id'):
            mark_user_offline(self.user_id, self.channel_name)

        if hasattr(self, 'group_name'):
            async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)

    def send_notification(self, event):
        payload = event.get('payload', {})
        self.send(text_data=json.dumps(payload))
