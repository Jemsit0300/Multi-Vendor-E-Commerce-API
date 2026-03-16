from rest_framework.permissions import BasePermission


class IsOwnerVendorOrAdmin(BasePermission):

    def has_object_permission(self, request, view, obj):

        if request.user.is_staff:
            return True

        if obj.user == request.user:
            return True

        for item in obj.items.all():
            if item.product.vendor == request.user:
                return True

        return False