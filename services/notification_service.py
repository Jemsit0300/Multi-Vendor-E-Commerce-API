from .models import Notification


class NotificationService:

    @staticmethod
    def notify_vendors(order):

        notified_vendors = set()

        for item in order.items.all():

            vendor = item.product.vendor

            if vendor.id in notified_vendors:
                continue

            Notification.objects.create(
                user=vendor,
                type="order",
                message=f"You received a new order #{order.id}"
            )

            notified_vendors.add(vendor.id)