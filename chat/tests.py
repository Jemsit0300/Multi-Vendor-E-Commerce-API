from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User

from .models import ChatRoom, Message


class ChatAPITestCase(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username='chat-customer',
            email='chat-customer@example.com',
            password='pass1234',
            role='customer',
        )
        self.vendor = User.objects.create_user(
            username='chat-vendor',
            email='chat-vendor@example.com',
            password='pass1234',
            role='vendor',
        )
        self.other_user = User.objects.create_user(
            username='chat-other',
            email='chat-other@example.com',
            password='pass1234',
            role='customer',
        )

        self.room = ChatRoom.objects.create(customer=self.customer, vendor=self.vendor)
        self.message = Message.objects.create(
            room=self.room,
            sender=self.customer,
            message='Hello vendor',
        )

    def test_room_list_requires_auth(self):
        response = self.client.get(reverse('chat-room-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_room_list_returns_only_user_rooms(self):
        ChatRoom.objects.create(customer=self.other_user, vendor=self.vendor)

        self.client.force_authenticate(self.customer)
        response = self.client.get(reverse('chat-room-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.room.id)

    def test_room_messages_returns_for_participant(self):
        self.client.force_authenticate(self.vendor)
        response = self.client.get(reverse('chat-room-messages', kwargs={'id': self.room.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.message.id)

    def test_room_messages_denies_non_participant(self):
        self.client.force_authenticate(self.other_user)
        response = self.client.get(reverse('chat-room-messages', kwargs={'id': self.room.id}))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
