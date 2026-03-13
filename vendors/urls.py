from django.urls import path
from .views import VendorMeView

urlpatterns = [
    path("api/vendors/me/", VendorMeView.as_view()),
]