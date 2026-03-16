from django.urls import path
from .views import mock_payment

urlpatterns = [
    path("api/orders/<int:order_id>/pay/", mock_payment),
]