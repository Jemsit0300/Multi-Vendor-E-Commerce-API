from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from orders.models import Order, OrderItem
from products.models import Product
from .models import Review

User = get_user_model()


class ReviewAPITestCase(APITestCase):
	def setUp(self):
		self.vendor = User.objects.create_user(
			username="vendor1",
			password="testpass123",
			role="vendor",
			email="vendor@example.com",
		)
		self.customer = User.objects.create_user(
			username="customer1",
			password="testpass123",
			role="customer",
			email="customer@example.com",
		)
		self.other_user = User.objects.create_user(
			username="customer2",
			password="testpass123",
			role="customer",
			email="customer2@example.com",
		)

		self.product = Product.objects.create(
			vendor=self.vendor,
			name="Keyboard",
			description="Mechanical keyboard",
			price="100.00",
			stock=10,
		)

		self.product_reviews_url = reverse(
			"product-reviews", kwargs={"id": self.product.id}
		)

	def _create_paid_order_for_customer(self):
		order = Order.objects.create(
			user=self.customer,
			total_price="100.00",
			status="pending_shipment",
		)
		OrderItem.objects.create(
			order=order,
			product=self.product,
			vendor=self.vendor,
			quantity=1,
			price="100.00",
		)

	def test_create_review_requires_purchase(self):
		self.client.force_authenticate(user=self.customer)

		payload = {"rating": 5, "comment": "Great product"}
		response = self.client.post(self.product_reviews_url, payload, format="json")

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
		self.assertEqual(Review.objects.count(), 0)

	def test_create_review_success_for_purchased_product(self):
		self._create_paid_order_for_customer()
		self.client.force_authenticate(user=self.customer)

		payload = {"rating": 5, "comment": "Great product"}
		response = self.client.post(self.product_reviews_url, payload, format="json")

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(Review.objects.count(), 1)
		self.assertEqual(Review.objects.first().user, self.customer)

	def test_user_can_only_create_one_review_per_product(self):
		self._create_paid_order_for_customer()
		Review.objects.create(
			user=self.customer,
			product=self.product,
			rating=4,
			comment="First review",
		)
		self.client.force_authenticate(user=self.customer)

		payload = {"rating": 5, "comment": "Second review"}
		response = self.client.post(self.product_reviews_url, payload, format="json")

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(Review.objects.filter(user=self.customer, product=self.product).count(), 1)

	def test_product_reviews_list(self):
		Review.objects.create(
			user=self.customer,
			product=self.product,
			rating=5,
			comment="Excellent",
		)
		response = self.client.get(self.product_reviews_url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 1)

	def test_delete_review_only_by_owner_or_admin(self):
		review = Review.objects.create(
			user=self.customer,
			product=self.product,
			rating=4,
			comment="Nice",
		)
		delete_url = reverse("review-delete", kwargs={"id": review.id})

		self.client.force_authenticate(user=self.other_user)
		forbidden_response = self.client.delete(delete_url)
		self.assertEqual(forbidden_response.status_code, status.HTTP_403_FORBIDDEN)

		self.client.force_authenticate(user=self.customer)
		success_response = self.client.delete(delete_url)
		self.assertEqual(success_response.status_code, status.HTTP_204_NO_CONTENT)
