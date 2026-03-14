from rest_framework import permissions

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
