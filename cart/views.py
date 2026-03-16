from django.shortcuts import render

from ecommerce.vendors import permissions
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from rest_framework import viewsets

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]