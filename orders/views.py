from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Order
from .serializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        user = self.request.user

        if user.is_staff:
            return Order.objects.all()

        if user.role == "vendor":
            return Order.objects.filter(
                items__product__vendor=user
            ).distinct()

        return Order.objects.filter(user=user)

    def perform_create(self, serializer):

        serializer.save(user=self.request.user)