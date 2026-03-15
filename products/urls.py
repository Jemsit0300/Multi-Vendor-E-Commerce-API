from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, ProductImageDeleteView, ProductImageView, ProductViewSet
from django.conf.urls.static import static



router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'products', ProductViewSet, basename='products')

urlpatterns = [
    path('', include(router.urls)),
   
    path(
        "api/products/<int:product_id>/images/",
        ProductImageView.as_view(),
    ),
   
    path(
        "api/products/<int:product_id>/images/<int:id>/",
        ProductImageDeleteView.as_view(),
    ),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)    