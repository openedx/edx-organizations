"""
Permissions for organization viewsets.
"""
from rest_framework.permissions import BasePermission


class UserIsStaff(BasePermission):
    """
    Custom Permission class to check user is a publisher user or a staff user.
    """
    def has_permission(self, request, view):
        if request.method == 'PUT':
            return request.user.is_staff or request.user.is_superuser
        return True
