from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Notification
from .serializers import NotificationSerializer


@receiver(post_save, sender=Notification)
def push_notification_realtime(sender, instance, created, **kwargs):
    if not created:
        return

    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    group_name = f'user_notifications_{instance.user_id}'
    payload = {
        'event': 'notification.created',
        'notification': NotificationSerializer(instance).data,
    }

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'send_notification',
            'payload': payload,
        },
    )
