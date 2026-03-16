from serializers import ModelSerializer
from .models import Cart, CartItem

class CartSerializer(ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'user']

class CartItemSerializer(ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity']