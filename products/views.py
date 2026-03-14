from .models import Category
from vendors.permissions import IsApprovedVendor
from .serializers import CategorySerializer, ProductSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics

class ProductCreateView(APIView):
    permission_classes = [IsApprovedVendor]

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(vendor=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
class CategoryView(generics.CreateAPIView): 
    queryset = Category.objects.all()
    serializer_class = CategorySerializer