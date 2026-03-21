from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from products.models import Product
from users.models import User
from .models import Wishlist


class WishlistAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="customer",
            email="customer@example.com",
            password="pass1234",
        )
        self.vendor = User.objects.create_user(
            username="vendor",
            email="vendor@example.com",
            password="pass1234",
            role="vendor",
        )
        self.product = Product.objects.create(
            vendor=self.vendor,
            name="Test Product",
            price="10.00",
            stock=5,
        )

    def test_auth_required_for_wishlist(self):
        response = self.client.get(reverse("wishlist-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_and_prevent_duplicate(self):
        self.client.force_authenticate(self.user)
        add_url = reverse("wishlist-add")

        first = self.client.post(add_url, {"product_id": self.product.id}, format="json")
        second = self.client.post(add_url, {"product_id": self.product.id}, format="json")

        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Wishlist.objects.filter(user=self.user, product=self.product).count(), 1)
