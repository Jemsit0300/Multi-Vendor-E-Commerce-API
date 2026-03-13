from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, permissions
from .models import Vendor
from .serializers import VendorSerializer
from .permissions import IsVendor

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