import django_filters
from django.core.cache import cache
from django.db.models import Avg
from rest_framework import filters
from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from vendors.permissions import IsApprovedVendor

from .models import Category, Product, ProductImage
from .permissions import CategoryPermission, ProductPermission
from .serializers import CategorySerializer, MultipleImageUploadSerializer, ProductImageSerializer, ProductSerializer
from rest_framework.generics import DestroyAPIView
from django_filters.rest_framework import DjangoFilterBackend


CACHE_TIMEOUT = 60 * 5
PRODUCT_LIST_VERSION_KEY = "product_list_version"
CATEGORY_LIST_VERSION_KEY = "category_list_version"
TOP_PRODUCTS_VERSION_KEY = "top_products_version"


def _get_cache_version(key):
    return cache.get_or_set(key, 1, None)


def _bump_cache_version(key):
    try:
        cache.incr(key)
    except ValueError:
        cache.set(key, 2, None)


def invalidate_product_related_cache():
    _bump_cache_version(PRODUCT_LIST_VERSION_KEY)
    _bump_cache_version(CATEGORY_LIST_VERSION_KEY)
    _bump_cache_version(TOP_PRODUCTS_VERSION_KEY)


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    rating = django_filters.NumberFilter(method='filter_by_rating')
    vendor = django_filters.CharFilter(field_name='vendor__username', lookup_expr='icontains')

    class Meta:
        model = Product
        fields = ['category', 'vendor']

    def filter_by_rating(self, queryset, name, value):
        return queryset.annotate(avg_rating=Avg('reviews__rating')).filter(avg_rating__gte=value)


class ProductCreateView(APIView):
    permission_classes = [IsApprovedVendor]

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(vendor=request.user)
            invalidate_product_related_cache()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [ProductPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'avg_rating']
    ordering = ['-created_at']

    def get_queryset(self):
        return (
            Product.objects
            .select_related('vendor')
            .prefetch_related('reviews')
            .annotate(avg_rating=Avg('reviews__rating'))
        )

    def list(self, request, *args, **kwargs):
        version = _get_cache_version(PRODUCT_LIST_VERSION_KEY)
        cache_key = f"product_list:v{version}:{request.get_full_path()}"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, CACHE_TIMEOUT)
        return response


    def perform_create(self, serializer):
        serializer.save(vendor=self.request.user)
        invalidate_product_related_cache()

    def perform_update(self, serializer):
        serializer.save()
        invalidate_product_related_cache()

    def perform_destroy(self, instance):
        instance.delete()
        invalidate_product_related_cache()

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [CategoryPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']

    def list(self, request, *args, **kwargs):
        version = _get_cache_version(CATEGORY_LIST_VERSION_KEY)
        cache_key = f"category_list:v{version}:{request.get_full_path()}"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, CACHE_TIMEOUT)
        return response


class TopProductsView(APIView):

    def get(self, request):
        version = _get_cache_version(TOP_PRODUCTS_VERSION_KEY)
        cache_key = f"top_products:v{version}:{request.get_full_path()}"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        limit = request.query_params.get('limit', 10)
        try:
            limit = max(int(limit), 1)
        except (TypeError, ValueError):
            limit = 10

        queryset = (
            Product.objects
            .select_related('vendor')
            .prefetch_related('reviews')
            .annotate(avg_rating=Avg('reviews__rating'))
            .order_by('-avg_rating', '-created_at')[:limit]
        )
        serializer = ProductSerializer(queryset, many=True)
        cache.set(cache_key, serializer.data, CACHE_TIMEOUT)
        return Response(serializer.data)

class ProductImageView(APIView):

    def get(self, request, product_id):
        images = ProductImage.objects.filter(product_id=product_id)
        serializer = ProductImageSerializer(images, many=True)
        return Response(serializer.data)

    def post(self, request, product_id):
        product = Product.objects.get(id=product_id)

        serializer = MultipleImageUploadSerializer(data=request.data)

        if serializer.is_valid():
            images = serializer.validated_data["images"]

            image_objs = [
                ProductImage(product=product, image=image)
                for image in images
            ]

            ProductImage.objects.bulk_create(image_objs)

            return Response({"message": "Images uploaded"}, status=201)

        return Response(serializer.errors, status=400)
    
class ProductImageDeleteView(DestroyAPIView):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    lookup_field = "id"