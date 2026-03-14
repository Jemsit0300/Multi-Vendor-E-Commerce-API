from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from vendors.permissions import IsApprovedVendor

from .models import Category
from .permissions import CategoryPermission
from .serializers import CategorySerializer, ProductSerializer


class ProductCreateView(APIView):
    permission_classes = [IsApprovedVendor]

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(vendor=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [CategoryPermission]