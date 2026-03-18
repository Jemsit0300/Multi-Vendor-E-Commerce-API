from rest_framework import serializers
from .models import Notification, Order, OrderItem

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'total_price', 'status', 'created_at']
        read_only_fields = ['total_price', 'status', 'created_at']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'vendor', 'quantity', 'price']
        read_only_fields = ['price']

class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = ["id", "message", "type", "is_read", "created_at"]