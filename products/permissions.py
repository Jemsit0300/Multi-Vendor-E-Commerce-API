from rest_framework import permissions

from vendors.permissions import IsApprovedVendor

class CategoryPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        action = getattr(view, "action", None)

        if action in ["list", "retrieve"]:
            return True

        if not request.user or not request.user.is_authenticated:
            return False

        if action == "create":
            return request.user.is_staff or request.user.is_superuser

        if action in ["update", "partial_update", "destroy"]:
            return request.user.is_superuser

        return False


class ProductPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        action = getattr(view, "action", None)

        if action in ["list", "retrieve"]:
            return True

        if action in ["create", "update", "partial_update", "destroy"]:
            return IsApprovedVendor().has_permission(request, view)

        return False

    def has_object_permission(self, request, view, obj):
        action = getattr(view, "action", None)

        if action in ["retrieve"]:
            return True

        if action in ["update", "partial_update", "destroy"]:
            return obj.vendor_id == request.user.id

        return True
