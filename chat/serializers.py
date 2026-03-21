from rest_framework import serializers

from .models import ChatRoom, Message
from .presence import is_user_online


class ChatRoomSerializer(serializers.ModelSerializer):
    customer_is_online = serializers.SerializerMethodField()
    vendor_is_online = serializers.SerializerMethodField()

    def get_customer_is_online(self, obj):
        return is_user_online(obj.customer_id)

    def get_vendor_is_online(self, obj):
        return is_user_online(obj.vendor_id)

    class Meta:
        model = ChatRoom
        fields = ['id', 'customer', 'vendor', 'customer_is_online', 'vendor_is_online']


class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'sender_username', 'message', 'created_at']
