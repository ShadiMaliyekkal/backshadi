from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Only owners can edit/delete. Read-only allowed for others.
    """
    def has_object_permission(self, request, view, obj):
        # Read-only: allow
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write: owner only
        return getattr(obj, 'author', None) == request.user
