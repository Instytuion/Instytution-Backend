from rest_framework.views import APIView
from accounts. models import CustomUser
from rest_framework.response import Response 
from rest_framework import status
from django.shortcuts import get_object_or_404


class BlockUnblockUserView(APIView):
    """API endpoint to block or unblock a user."""

    def patch(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])
        return Response({"status": "success", "is_active": user.is_active}, status=status.HTTP_200_OK)

