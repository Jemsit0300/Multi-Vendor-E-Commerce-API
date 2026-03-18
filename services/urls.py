from django.urls import path
from .views import VendorNotificationListView

urlpatterns = [
    path("vendors/notifications/", VendorNotificationListView.as_view()),
]