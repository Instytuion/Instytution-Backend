from django.urls import path
from .views import *


urlpatterns = [
    path('user-block-unblock/<int:user_id>/', BlockUnblockUserView.as_view(), name='block_unblock'),
    path('instructore-block-unblock/<int:user_id>/', InstructoreBlockUnblock.as_view(), name='block_unblock_instructor'),
    path('users/role/<str:role>/', UserListByRoleView.as_view(), name='user-list-by-role'),
    path('instructors/<str:role>/', InstructorsLIstView.as_view(), name='instructors-list'),
]