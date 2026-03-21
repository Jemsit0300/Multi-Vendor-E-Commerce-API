from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer


class ChatRoomListAPIView(generics.ListAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return ChatRoom.objects.filter(Q(customer=user) | Q(vendor=user)).order_by('-id')


class RoomMessageListAPIView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        room = get_object_or_404(
            ChatRoom.objects.filter(Q(customer=user) | Q(vendor=user)),
            id=self.kwargs['id'],
        )
        return Message.objects.filter(room=room).select_related('sender').order_by('created_at')
