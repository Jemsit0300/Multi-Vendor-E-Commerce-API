from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from vendors.permissions import IsApprovedVendor

from .models import Category, Product
from .permissions import CategoryPermission, ProductPermission
from .serializers import CategorySerializer, ProductSerializer


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

    def perform_create(self, serializer):
        serializer.save(vendor=self.request.user)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [CategoryPermission]

