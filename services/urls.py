from django.urls import path
from .views import NotificationListAPIView, NotificationReadAPIView, VendorNotificationListView

urlpatterns = [
    path("vendors/notifications/", VendorNotificationListView.as_view()),
    path("api/notifications/", NotificationListAPIView.as_view(), name="notifications-list"),
    path("api/notifications/<int:id>/read/", NotificationReadAPIView.as_view(), name="notifications-read"),
]