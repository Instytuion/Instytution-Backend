from rest_framework import permissions

class IsAdminAndAuthenticated(permissions.BasePermission):
    """
    Custom permission to grant access only to users with the 'admin' role and who are authenticated.
    """

    def has_permission(self, request,view):
        return request.user.is_authenticated and request.user.role == 'admin'
    

class IsCourseAdmin(permissions.BasePermission):
    """
    Custom permission to grant access only to users with the 'course_admin' role and who are authenticated.
    """
    def has_permission(self, request,view):
        return request.user.is_authenticated and request.user.role == 'course_admin'
    

class IsShopAdmin(permissions.BasePermission):
    """
    Custom permission to grant access only to users with the 'shop_admin' role and who are authenticated.
    """
    def has_permission(self, request,view):
        return request.user.is_authenticated and request.user.role == 'shop_admin'