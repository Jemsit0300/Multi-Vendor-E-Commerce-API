from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Product

from .models import Wishlist
from .serializers import WishlistSerializer


class WishlistListAPIView(ListAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).select_related("product", "product__vendor")


class WishlistAddAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get("product") or request.data.get("product_id")
        if not product_id:
            return Response({"detail": "product_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, id=product_id)
        item, created = Wishlist.objects.get_or_create(user=request.user, product=product)

        if not created:
            return Response(
                {"detail": "Product is already in wishlist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = WishlistSerializer(item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WishlistRemoveAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        item = get_object_or_404(Wishlist, id=id, user=request.user)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
