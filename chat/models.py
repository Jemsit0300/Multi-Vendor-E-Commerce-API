from django.conf import settings
from django.db import models


class ChatRoom(models.Model):
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_rooms',
    )
    vendor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vendor_rooms',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['customer', 'vendor'], name='unique_customer_vendor_room'),
        ]

    def __str__(self):
        return f'Room {self.id}: {self.customer_id}->{self.vendor_id}'


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Message {self.id} in room {self.room_id}'
