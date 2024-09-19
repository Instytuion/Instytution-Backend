from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from accounts. models import CustomUser
from rest_framework.response import Response 
from rest_framework import status
from django.shortcuts import get_object_or_404
from accounts.serializers import UserSerializer
from accounts.permissions import IsAdminAndAuthenticated
from .pagination import StandardResultsSetPagination
from rest_framework import filters
from rest_framework.exceptions import ValidationError

class BlockUnblockUserView(APIView):
    """API endpoint to block or unblock a user."""

    def patch(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])
        return Response({"status": "success", "is_active": user.is_active}, status=status.HTTP_200_OK)

class UserListByRoleView(ListAPIView):
    """To list users by their roles with search and pagination support."""

    serializer_class = UserSerializer
    permission_classes = [IsAdminAndAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['email', 'first_name', 'last_name']

    def get_queryset(self):
        role = self.kwargs['role']

        valid_roles = CustomUser.get_valid_roles()
        if role not in valid_roles:
            raise ValidationError({'error': 'Invalid role provided.'})

        return CustomUser.objects.filter(role=role)

