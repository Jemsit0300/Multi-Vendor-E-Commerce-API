from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Order, OrderItem
from .serializers import OrderSerializer
from .services import PaymentService

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
            return Response({"error": "Cart not found"}, status=400)

        if not cart.items.exists():
            return Response({"error": "Cart is empty"}, status=400)

        # Stock check
        for item in cart.items.all():
            if item.product.stock < item.quantity:
                return Response(
                    {"error": f"{item.product.name} out of stock"},
                    status=400
                )

        # Create order
        order = Order.objects.create(
            user=request.user,
            status="created"
        )

        # Move cart → order
        for item in cart.items.all():

            product = item.product

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item.quantity,
                price=product.price
            )

            # Reduce stock
            product.stock -= item.quantity
            product.save()

        # Clear cart
        cart.items.all().delete()

        serializer = OrderSerializer(order)

        return Response(serializer.data, status=201)

    # 💳 MOCK PAYMENT ENDPOINT
    @action(detail=True, methods=["post"])
    def pay(self, request, pk=None):

        try:
            order = self.get_queryset().get(pk=pk)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        # Prevent duplicate payment
        if order.status in ["paid", "pending_shipment"]:
            return Response(
                {"error": "Order already paid"},
                status=400
            )

        # 🔹 Call mock payment service
        success = PaymentService.process_payment(order, request.data)

        if success:
            order.status = "pending_shipment"   # or "paid"
            order.save()

            return Response({
                "message": "Payment successful",
                "order_status": order.status
            })

        else:
            order.status = "payment_failed"
            order.save()

            return Response({
                "message": "Payment failed",
                "order_status": order.status
            }, status=400)