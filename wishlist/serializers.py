from rest_framework import serializers

from products.serializers import ProductSerializer

from .models import Wishlist


class WishlistSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Wishlist
        fields = ("id", "product", "product_id", "created_at")
        read_only_fields = ("id", "product", "created_at")
