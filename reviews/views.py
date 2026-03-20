from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import DestroyAPIView, ListCreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from orders.models import OrderItem
from products.models import Product

from .models import Review
from .serializers import ReviewSerializer

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class ProductReviewListCreateAPIView(ListCreateAPIView):
	serializer_class = ReviewSerializer
	filter_backends = [DjangoFilterBackend]
	filterset_fields = ['rating']

	def get_permissions(self):
		if self.request.method == "POST":
			return [IsAuthenticated()]
		return [AllowAny()]

	def get_queryset(self):
		product = get_object_or_404(Product, id=self.kwargs["id"])
		return Review.objects.filter(product=product).order_by("-created_at")

	def create(self, request, *args, **kwargs):
		product = get_object_or_404(Product, id=kwargs["id"])

		if Review.objects.filter(user=request.user, product=product).exists():
			return Response(
				{"detail": "You have already reviewed this product."},
				status=status.HTTP_400_BAD_REQUEST,
			)

		has_purchased = OrderItem.objects.filter(
			order__user=request.user,
			order__status__in=["paid", "pending_shipment"],
			product=product,
		).exists()

		if not has_purchased:
			return Response(
				{"detail": "You can review only products you purchased."},
				status=status.HTTP_403_FORBIDDEN,
			)

		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save(user=request.user, product=product)
		headers = self.get_success_headers(serializer.data)
		return Response(
			serializer.data,
			status=status.HTTP_201_CREATED,
			headers=headers,
		)


class IsReviewOwnerOrAdminMixin:
	def delete(self, request, *args, **kwargs):
		review = self.get_object()
		if review.user != request.user and not request.user.is_staff:
			return Response(
				{"detail": "You do not have permission to delete this review."},
				status=status.HTTP_403_FORBIDDEN,
			)
		return super().delete(request, *args, **kwargs)


class ReviewDeleteAPIView(IsReviewOwnerOrAdminMixin, DestroyAPIView):
	permission_classes = [IsAuthenticated]
	serializer_class = ReviewSerializer
	queryset = Review.objects.all()
	lookup_field = "id"
