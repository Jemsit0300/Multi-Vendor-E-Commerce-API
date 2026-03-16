import random
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Order


@api_view(["POST"])
def mock_payment(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)

    # simulate payment success or failure
    payment_success = random.choice([True, False])

    if payment_success:
        order.status = "pending_shipment"
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
        }, status=status.HTTP_400_BAD_REQUEST)