from django.urls import path

from .views import ChatRoomListAPIView, RoomMessageListAPIView


urlpatterns = [
    path('api/chat/rooms/', ChatRoomListAPIView.as_view(), name='chat-room-list'),
    path('api/chat/rooms/<int:id>/messages/', RoomMessageListAPIView.as_view(), name='chat-room-messages'),
]
