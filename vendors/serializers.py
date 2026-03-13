from rest_framework import serializers
from .models import Vendor

class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ('id', 'user', 'store_name', 'store_description', 'store_logo', 'is_approved', 'created_at')
        read_only_fields = ('user', 'is_approved', 'created_at')
