from rest_framework.permissions import BasePermission

class IsVendor(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'vendor'


class IsApprovedVendor(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.role != "vendor":
            return False

        vendor_profile = getattr(request.user, "vendor_profile", None)
        if vendor_profile is None:
            return False

        return vendor_profile.is_approved