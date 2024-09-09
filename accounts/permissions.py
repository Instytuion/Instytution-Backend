from rest_framework import permissions

class IsAdminAndAuthenticated(permissions.BasePermission):
    """
    Custom permission to grant access only to users with the 'admin' role and who are authenticated.
    """

    def has_permission(self, request,):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return getattr(request.user, 'role', None) == 'admin'
