from django.urls import path
from .views import CategoryView, ProductCreateView


urlpatterns = [
    path('create/', ProductCreateView.as_view(), name='product-create'),
    path('category/', CategoryView.as_view(), name='category-create'),
]
