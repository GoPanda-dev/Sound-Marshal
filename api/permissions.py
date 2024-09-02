from rest_framework import permissions
from core.models import Track, Comment

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to edit or delete it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD, or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # For objects with different ownership attributes
        if isinstance(obj, Track):
            return obj.artist == request.user or request.user.is_staff or request.user.is_superuser
        elif isinstance(obj, Comment):
            return obj.user == request.user or request.user.is_staff or request.user.is_superuser
        else:
            # Default to denying access if ownership isn't clear
            return False
