from django.urls import path
from .views import VendorListCreateView, VendorMeView, VendorRetrieveUpdateDestroyView

urlpatterns = [
    path('', VendorListCreateView.as_view(), name='vendor-list-create'),
    path('<int:pk>/', VendorRetrieveUpdateDestroyView.as_view(), name='vendor-detail'),
    path('me/', VendorMeView.as_view(), name='vendor-me'),
]