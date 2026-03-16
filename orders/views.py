from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Order, OrderItem
from .serializers import OrderSerializer
from cart.models import Cart


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

    def create(self, request):

        cart = Cart.objects.filter(user=request.user).first()

        if not cart:
            return Response(
                {"error": "Cart not found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not cart.items.exists():
            return Response(
                {"error": "Cart is empty"},
                status=status.HTTP_400_BAD_REQUEST
            )

        for item in cart.items.all():
            if item.product.stock < item.quantity:
                return Response(
                    {"error": f"{item.product.name} out of stock"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        order = Order.objects.create(
            user=request.user,
            status="pending"
        )

        for item in cart.items.all():

            product = item.product

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item.quantity,
                price=product.price
            )

            product.stock -= item.quantity
            product.save()

        cart.items.all().delete()

        serializer = OrderSerializer(order)

        return Response(serializer.data, status=status.HTTP_201_CREATED)