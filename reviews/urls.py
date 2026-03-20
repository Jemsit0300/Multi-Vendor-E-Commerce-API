from django.urls import path

from .views import ProductReviewListCreateAPIView, ReviewDeleteAPIView


urlpatterns = [
    path(
        "api/products/<int:id>/reviews/",
        ProductReviewListCreateAPIView.as_view(),
        name="product-reviews",
    ),
    path(
        "api/reviews/<int:id>/",
        ReviewDeleteAPIView.as_view(),
        name="review-delete",
    ),
]
