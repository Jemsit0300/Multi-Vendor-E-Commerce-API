from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Order, OrderItem
from .serializers import OrderSerializer
from .services import PaymentService
from .email_service import EmailService
from services.notification_service import NotificationService
from services.stock_service import StockService

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

        order = Order.objects.create(
            user=request.user,
            status="created"
        )

        for item in cart.items.all():

            product = item.product

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item.quantity,
                price=product.price
            )

        cart.items.all().delete()

        serializer = OrderSerializer(order)

        return Response(serializer.data, status=201)

    @action(detail=True, methods=["post"])
    def pay(self, request, pk=None):

        try:
            order = self.get_queryset().get(pk=pk)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        if order.status in ["paid", "pending_shipment"]:
            return Response(
                {"error": "Order already paid"},
                status=400
            )

        valid, product_name = StockService.validate_stock(order)

        if not valid:
            order.status = "payment_failed"
            order.save()

            return Response({
                "error": f"{product_name} is out of stock",
                "order_status": order.status
            }, status=400)

        success = PaymentService.process_payment(order, request.data)

        if not success:
            order.status = "payment_failed"
            order.save()

            return Response({
                "error": "Payment failed",
                "order_status": order.status
            }, status=400)

        try:
            StockService.reduce_stock(order)
        except Exception as e:
            order.status = "payment_failed"
            order.save()

            return Response({
                "error": str(e),
                "order_status": order.status
            }, status=400)

        order.status = "pending_shipment"
        order.save()

        EmailService.send_order_confirmation(order)
        NotificationService.notify_vendors(order)

        return Response({
            "message": "Payment successful",
            "order_status": order.status
        })