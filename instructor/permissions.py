from rest_framework import permissions

class IsInstructor(permissions.BasePermission):
    """
    Custom permission to grant access only to users with the 'instructor' role and who is authenticated.
    """
    def has_permission(self, request,view):
        return request.user.is_authenticated and request.user.role == 'instructor'