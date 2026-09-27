from rest_framework.permissions import BasePermission

from .models import Company


class IsAdminUser(BasePermission):
    message = 'Admin access is required.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, 'company')
            and request.user.company.role == Company.Role.ADMIN
        )