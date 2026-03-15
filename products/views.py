from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from vendors.permissions import IsApprovedVendor

from .models import Category, Product, ProductImage
from .permissions import CategoryPermission, ProductPermission
from .serializers import CategorySerializer, MultipleImageUploadSerializer, ProductImageSerializer, ProductSerializer
from rest_framework.generics import DestroyAPIView
from django_filters.rest_framework import DjangoFilterBackend


class ProductCreateView(APIView):
    permission_classes = [IsApprovedVendor]

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(vendor=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [ProductPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'price']


    def perform_create(self, serializer):
        serializer.save(vendor=self.request.user)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [CategoryPermission]

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