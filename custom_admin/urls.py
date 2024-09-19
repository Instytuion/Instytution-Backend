from django.urls import path
from .views import *


urlpatterns = [
    path('user-block-unblock/<int:user_id>/', BlockUnblockUserView.as_view(), name='block_unblock'),
    path('users/role/<str:role>/', UserListByRoleView.as_view(), name='user-list-by-role'),
]