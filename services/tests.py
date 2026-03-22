from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User

from .models import Notification


class NotificationAPITestCase(APITestCase):
	def _get_results(self, response):
		if isinstance(response.data, dict) and "results" in response.data:
			return response.data["results"]
		return response.data

	def setUp(self):
		self.user = User.objects.create_user(
			username="notify-user",
			email="notify-user@example.com",
			password="pass1234",
		)
		self.other_user = User.objects.create_user(
			username="other-user",
			email="other-user@example.com",
			password="pass1234",
		)

		self.notification = Notification.objects.create(
			user=self.user,
			type="order",
			message="Order created",
		)

	def test_notifications_list_requires_auth(self):
		response = self.client.get(reverse("notifications-list"))
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_notifications_list_returns_only_user_notifications(self):
		Notification.objects.create(
			user=self.other_user,
			type="order",
			message="Other message",
		)

		self.client.force_authenticate(self.user)
		response = self.client.get(reverse("notifications-list"))
		results = self._get_results(response)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(results), 1)
		self.assertEqual(results[0]["id"], self.notification.id)

	def test_mark_notification_as_read(self):
		self.client.force_authenticate(self.user)
		url = reverse("notifications-read", kwargs={"id": self.notification.id})

		response = self.client.put(url, {}, format="json")
		self.notification.refresh_from_db()

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertTrue(self.notification.is_read)

	def test_cannot_mark_other_user_notification(self):
		other_notification = Notification.objects.create(
			user=self.other_user,
			type="order",
			message="Other private notification",
		)

		self.client.force_authenticate(self.user)
		url = reverse("notifications-read", kwargs={"id": other_notification.id})
		response = self.client.put(url, {}, format="json")

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
