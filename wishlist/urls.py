from django.urls import path

from .views import WishlistAddAPIView, WishlistListAPIView, WishlistRemoveAPIView

urlpatterns = [
    path("api/wishlist/add/", WishlistAddAPIView.as_view(), name="wishlist-add"),
    path("api/wishlist/", WishlistListAPIView.as_view(), name="wishlist-list"),
    path("api/wishlist/remove/<int:id>/", WishlistRemoveAPIView.as_view(), name="wishlist-remove"),
]
