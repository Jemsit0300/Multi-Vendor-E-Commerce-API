from django.db.models.signals import post_save
from django.dispatch import receiver

from services.notification_service import NotificationService

from .models import Order


@receiver(post_save, sender=Order)
def notify_on_order_created(sender, instance, created, **kwargs):
    if created:
        NotificationService.notify_order_created(instance)
