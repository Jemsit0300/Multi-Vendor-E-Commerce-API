from rest_framework import serializers
from .models import Vendor
from users.models import User

class VendorSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True,
        required=False,
    )
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Vendor
        fields = ('id', 'user', 'user_id', 'store_name', 'store_description', 'store_logo', 'is_approved', 'created_at')
        read_only_fields = ('user', 'is_approved', 'created_at')
