from .models import Notification


class NotificationService:

    @staticmethod
    def notify_order_created(order):
        Notification.objects.create(
            user=order.user,
            type="order",
            message=f"Your order #{order.id} has been created.",
        )

    @staticmethod
    def notify_payment_success(order):
        Notification.objects.create(
            user=order.user,
            type="order",
            message=f"Payment successful for order #{order.id}.",
        )

    @staticmethod
    def notify_order_shipped(order):
        Notification.objects.create(
            user=order.user,
            type="order",
            message=f"Your order #{order.id} has been shipped.",
        )

    @staticmethod
    def notify_vendors_new_order(order):

        notified_vendors = set()

        for item in order.items.all():

            vendor = item.product.vendor

            if vendor.id in notified_vendors:
                continue

            NotificationService.notify_vendor_new_order(order, vendor)

            notified_vendors.add(vendor.id)

    @staticmethod
    def notify_vendor_new_order(order, vendor):
        Notification.objects.create(
            user=vendor,
            type="order",
            message=f"You received a new order #{order.id}",
        )

    @staticmethod
    def notify_vendors(order):
        # Backward-compatible alias for previous calls.
        NotificationService.notify_vendors_new_order(order)