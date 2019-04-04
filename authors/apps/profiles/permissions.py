from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Class restricting write permissions to only the owner
    of the profile
    """

    def has_permissions(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        username = view.kwargs.get('username')
        return request.user.username == username
