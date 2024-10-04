from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from accounts. models import CustomUser
from rest_framework.response import Response 
from rest_framework import status
from django.shortcuts import get_object_or_404
from accounts.serializers import UserSerializer
from accounts.permissions import IsAdminAndAuthenticated,IsCourseAdmin
from .pagination import StandardResultsSetPagination
from rest_framework import filters
from rest_framework.exceptions import ValidationError

class BlockUnblockUserViewBaseClass(APIView):
    """Base class for blocking or unblocking users."""
    permission_classes = []
    def patch(self, request, user_id):
        self.validate(request, user_id)  
        user = get_object_or_404(CustomUser, id=user_id)
        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])
        return Response({"status": "success", "is_active": user.is_active}, status=status.HTTP_200_OK)
    

class BlockUnblockUserView(BlockUnblockUserViewBaseClass):
    """API endpoint to block or unblock a user.(without instructore)"""
    permission_classes = [IsAdminAndAuthenticated]
    def validate(self):
        pass


class InstructoreBlockUnblock(BlockUnblockUserViewBaseClass):
    """API endpoint to block or unblock an instructor"""
    permission_classes = [IsCourseAdmin]

    def validate(self, request, user_id):
        user = get_object_or_404(CustomUser.objects.only('id', 'role'), id=user_id)
        if user.role != 'instructor':
            raise ValidationError({'error': 'Only instructors can be blocked or unblocked.'})


class UserListByRoleViewBaseClass(ListAPIView):
    """To list users by their roles with search and pagination support."""

    serializer_class = UserSerializer
    permission_classes = []
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['email', 'first_name', 'last_name']

    def get_queryset(self):
        self.validate()
        role = self.kwargs['role']

        valid_roles = CustomUser.get_valid_roles()
        if role not in valid_roles:
            raise ValidationError({'error': 'Invalid role provided.'})

        return CustomUser.objects.filter(role=role)



class UserListByRoleView(UserListByRoleViewBaseClass):
    """To list users by their roles with search and pagination support. (without Instructore)"""
    permission_classes = [IsAdminAndAuthenticated]
    def validate(self):
        pass

class InstructorsLIstView(UserListByRoleViewBaseClass):
    permission_classes = [IsCourseAdmin]
    def validate(self):
        role = self.kwargs['role']
        if role != 'instructor':
            raise ValidationError({'error': 'You DO not have permission to interact with this user'})