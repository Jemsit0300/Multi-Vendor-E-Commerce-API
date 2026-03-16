from serializers import ModelSerializer
from .models import Cart, CartItem

class CartSerializer(ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'user']

