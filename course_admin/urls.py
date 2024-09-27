from django.urls import path
from .views import *

urlpatterns = [
    path('courses/', CourseCreateView.as_view(), name='course-create'),     
    path('courses/<str:course_name>/', CourseCreateView.as_view(), name='course-detail'),  
    path('courses/update/<str:course_name>/', CourseUpdateView.as_view(), name='course-update'),
]