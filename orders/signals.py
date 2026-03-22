from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from chat.models import ChatRoom, Message
from orders.models import OrderItem
from services.notification_service import NotificationService

from .models import Order


@receiver(post_save, sender=Order)
def notify_on_order_created(sender, instance, created, **kwargs):
    if created:
        NotificationService.notify_order_created(instance)


@receiver(post_save, sender=OrderItem)
def notify_vendor_on_order_item_created(sender, instance, created, **kwargs):
    if not created:
        return

    order = instance.order
    vendor = instance.product.vendor

    vendor_was_already_in_order = OrderItem.objects.filter(
        order=order,
        product__vendor=vendor,
    ).exclude(pk=instance.pk).exists()
    if vendor_was_already_in_order:
        return

    def _dispatch_vendor_automation():
        NotificationService.notify_vendor_new_order(order, vendor)
        room, _ = ChatRoom.objects.get_or_create(customer=order.user, vendor=vendor)
        Message.objects.create(
            room=room,
            sender=order.user,
            message=f"Customer created order #{order.id}.",
        )

    transaction.on_commit(_dispatch_vendor_automation)
