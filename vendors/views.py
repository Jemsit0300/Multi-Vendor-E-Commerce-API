from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Vendor
from .serializers import VendorSerializer
from .permissions import IsVendor
from django_filters.rest_framework import DjangoFilterBackend


class IsVendorOwnerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_staff or request.user.role == "vendor"
        )

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.user_id == request.user.id


class VendorListCreateView(generics.ListCreateAPIView):
    serializer_class = VendorSerializer
    permission_classes = [IsVendorOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']

    def get_queryset(self):
        if self.request.user.is_staff:
            return Vendor.objects.all().order_by("-created_at")
        return Vendor.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        if self.request.user.is_staff:
            return serializer.save()

        if Vendor.objects.filter(user=self.request.user).exists():
            raise ValidationError({"detail": "Vendor profile already exists."})

        serializer.save(user=self.request.user)


class VendorRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    permission_classes = [IsVendorOwnerOrAdmin]

class VendorMeView(APIView):
    permission_classes = [IsVendor]

    def get(self, request):
        vendor = Vendor.objects.filter(user=request.user).first()
        if not vendor:
            return Response({"detail": "Vendor profile not found."}, status=404)
        serializer = VendorSerializer(vendor)
        return Response(serializer.data)

    def put(self, request):
        vendor = Vendor.objects.filter(user=request.user).first()
        if not vendor:
            return Response({"detail": "Vendor profile not found."}, status=404)
        serializer = VendorSerializer(vendor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)