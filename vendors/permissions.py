from rest_framework.permissions import BasePermission

class IsVendor(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'vendor'