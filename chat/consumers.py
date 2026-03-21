import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from .models import ChatRoom, Message


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            self.close()
            return

        room_id = self.scope['url_route']['kwargs']['room_id']
        room = ChatRoom.objects.filter(id=room_id).first()

        if room is None:
            self.close()
            return

        if user.id not in [room.customer_id, room.vendor_id]:
            self.close()
            return

        self.room = room
        self.room_group_name = f'chat_room_{room.id}'

        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)

    def receive(self, text_data):
        user = self.scope.get('user')
        if not user or not user.is_authenticated or not hasattr(self, 'room'):
            return

        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        message_text = (data.get('message') or '').strip()
        if not message_text:
            return

        message = Message.objects.create(
            room=self.room,
            sender=user,
            message=message_text,
        )

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'payload': {
                    'id': message.id,
                    'room': self.room.id,
                    'sender': user.id,
                    'message': message.message,
                    'created_at': message.created_at.isoformat(),
                },
            },
        )

    def chat_message(self, event):
        self.send(text_data=json.dumps(event['payload']))
