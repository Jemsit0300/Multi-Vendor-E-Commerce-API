from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product
from vendors.models import Vendor
from django.db.models import Sum, F
from datetime import timedelta
from django.utils import timezone

User = get_user_model()

class Order(models.Model):

    STATUS_CHOICES = [
        ("created", "Created"),
        ("pending_shipment", "Pending Shipment"),
        ("paid", "Paid"),
        ("payment_failed", "Payment Failed"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id}"

    def get_total_price(self):
        return self.items.aggregate(
            total=Sum(F("price") * F("quantity"))
        )["total"] or 0

    def get_estimated_delivery(self):
        return timezone.now() + timedelta(days=5)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

class Notification(models.Model):

    TYPE_CHOICES = [
        ("order", "Order"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user}"