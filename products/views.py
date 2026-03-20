import django_filters
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
        return Product.objects.annotate(avg_rating=Avg('reviews__rating'))


    def perform_create(self, serializer):
        serializer.save(vendor=self.request.user)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [CategoryPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']

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