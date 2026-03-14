from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, ProductCreateView, ProductViewSet


router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'products', ProductViewSet, basename='products')

urlpatterns = [
    path('create/', ProductCreateView.as_view(), name='product-create'),
    path('', include(router.urls)),
]
