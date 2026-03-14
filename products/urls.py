from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, ProductCreateView


router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='categories')


urlpatterns = [
    path('create/', ProductCreateView.as_view(), name='product-create'),
    path('', include(router.urls)),
]
