from django.test import TestCase

from chat.models import ChatRoom, Message
from products.models import Product
from services.models import Notification
from users.models import User
from vendors.models import Vendor

from .models import Order, OrderItem


class OrderSignalAutomationTestCase(TestCase):
	def setUp(self):
		self.customer = User.objects.create_user(
			username="signal-customer",
			email="signal-customer@example.com",
			password="pass1234",
			role="customer",
		)
		self.vendor = User.objects.create_user(
			username="signal-vendor",
			email="signal-vendor@example.com",
			password="pass1234",
			role="vendor",
		)
		self.product = Product.objects.create(
			vendor=self.vendor,
			name="Signal Product",
			price="25.00",
			stock=10,
		)
		self.vendor_profile = Vendor.objects.create(
			user=self.vendor,
			store_name="Signal Vendor Store",
			is_approved=True,
		)

	def test_order_post_save_sends_customer_notification(self):
		order = Order.objects.create(
			user=self.customer,
			status="created",
			total_price="25.00",
		)

		self.assertTrue(
			Notification.objects.filter(
				user=self.customer,
				type="order",
				message=f"Your order #{order.id} has been created.",
			).exists()
		)

	def test_order_item_post_save_sends_vendor_notification_and_message_once(self):
		order = Order.objects.create(
			user=self.customer,
			status="created",
			total_price="50.00",
		)

		with self.captureOnCommitCallbacks(execute=True):
			OrderItem.objects.create(
				order=order,
				product=self.product,
				vendor=self.vendor_profile,
				quantity=1,
				price="25.00",
			)
			# Same vendor appears twice in the order, automation should still run once.
			OrderItem.objects.create(
				order=order,
				product=self.product,
				vendor=self.vendor_profile,
				quantity=1,
				price="25.00",
			)

		self.assertEqual(
			Notification.objects.filter(
				user=self.vendor,
				type="order",
				message=f"You received a new order #{order.id}",
			).count(),
			1,
		)

		room = ChatRoom.objects.get(customer=self.customer, vendor=self.vendor)
		self.assertEqual(
			Message.objects.filter(
				room=room,
				sender=self.customer,
				message=f"Customer created order #{order.id}.",
			).count(),
			1,
		)

