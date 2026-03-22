import random
from contextlib import contextmanager
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models.signals import post_save

from orders.models import Order, OrderItem
from orders.signals import notify_on_order_created, notify_vendor_on_order_item_created
from products.models import Product
from services.models import Notification
from services.signals import push_notification_realtime
from vendors.models import Vendor


User = get_user_model()


@contextmanager
def muted_demo_signals():
    """Temporarily mute order/notification signals to keep seeding deterministic."""
    post_save.disconnect(notify_on_order_created, sender=Order)
    post_save.disconnect(notify_vendor_on_order_item_created, sender=OrderItem)
    post_save.disconnect(push_notification_realtime, sender=Notification)
    try:
        yield
    finally:
        post_save.connect(notify_on_order_created, sender=Order)
        post_save.connect(notify_vendor_on_order_item_created, sender=OrderItem)
        post_save.connect(push_notification_realtime, sender=Notification)


class Command(BaseCommand):
    help = "Seed demo data: 5 vendors, 20 products, 10 orders"

    def add_arguments(self, parser):
        parser.add_argument("--vendors", type=int, default=5)
        parser.add_argument("--products", type=int, default=20)
        parser.add_argument("--orders", type=int, default=10)

    def handle(self, *args, **options):
        vendor_target = max(options["vendors"], 0)
        product_target = max(options["products"], 0)
        order_target = max(options["orders"], 0)

        with transaction.atomic(), muted_demo_signals():
            vendor_users, created_vendors = self._ensure_vendors(vendor_target)
            products, created_products = self._ensure_products(product_target, vendor_users)
            created_orders = self._create_orders(order_target, products)

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
        self.stdout.write(f"Vendors created: {created_vendors}")
        self.stdout.write(f"Products created: {created_products}")
        self.stdout.write(f"Orders created: {created_orders}")

    def _ensure_vendors(self, target_count):
        vendor_users = []
        created = 0

        for idx in range(1, target_count + 1):
            username = f"demo_vendor_{idx}"
            email = f"demo_vendor_{idx}@example.com"

            user, user_created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "role": "vendor",
                    "is_verified": True,
                },
            )
            if user_created:
                user.set_password("DemoPass123!")
                user.save(update_fields=["password"])

            if user.role != "vendor":
                user.role = "vendor"
                user.save(update_fields=["role"])

            _, vendor_created = Vendor.objects.get_or_create(
                user=user,
                defaults={
                    "store_name": f"Demo Store {idx}",
                    "store_description": f"Sample vendor store #{idx}",
                    "is_approved": True,
                },
            )
            if vendor_created:
                created += 1

            vendor_users.append(user)

        return vendor_users, created

    def _ensure_products(self, target_count, vendor_users):
        if not vendor_users:
            return [], 0

        categories = ["Electronics", "Home", "Fashion", "Books", "Sports"]
        created = 0
        products = []

        for idx in range(1, target_count + 1):
            vendor_user = vendor_users[(idx - 1) % len(vendor_users)]
            name = f"Demo Product {idx:02d}"
            price = Decimal(random.randint(15, 500)) + Decimal("0.99")

            product, was_created = Product.objects.get_or_create(
                name=name,
                defaults={
                    "vendor": vendor_user,
                    "description": f"Demo product description for item {idx}",
                    "price": price,
                    "stock": random.randint(10, 100),
                    "category": categories[(idx - 1) % len(categories)],
                },
            )
            if was_created:
                created += 1

            if product.vendor_id != vendor_user.id:
                product.vendor = vendor_user
                product.save(update_fields=["vendor"])

            products.append(product)

        return products, created

    def _create_orders(self, target_count, products):
        if not products:
            return 0

        customers = []
        for idx in range(1, max(target_count, 5) + 1):
            username = f"demo_customer_{idx}"
            email = f"demo_customer_{idx}@example.com"
            customer, was_created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "role": "customer",
                    "is_verified": True,
                },
            )
            if was_created:
                customer.set_password("DemoPass123!")
                customer.save(update_fields=["password"])
            if customer.role != "customer":
                customer.role = "customer"
                customer.save(update_fields=["role"])
            customers.append(customer)

        created_orders = 0
        order_statuses = ["created", "pending_shipment", "paid", "shipped"]

        for idx in range(1, target_count + 1):
            customer = customers[(idx - 1) % len(customers)]
            status = order_statuses[(idx - 1) % len(order_statuses)]

            order = Order.objects.create(
                user=customer,
                total_price=Decimal("0.00"),
                status=status,
            )

            item_count = random.randint(1, 3)
            selected_products = random.sample(products, k=min(item_count, len(products)))
            total = Decimal("0.00")

            for product in selected_products:
                qty = random.randint(1, 3)
                unit_price = product.price
                line_total = unit_price * qty
                total += line_total

                vendor_profile = Vendor.objects.get(user=product.vendor)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    vendor=vendor_profile,
                    quantity=qty,
                    price=unit_price,
                )

            order.total_price = total
            order.save(update_fields=["total_price"])
            created_orders += 1

        return created_orders
