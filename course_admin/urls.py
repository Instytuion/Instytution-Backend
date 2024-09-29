from django.urls import path
from .views import *

urlpatterns = [
    path('courses/', CourseCreateView.as_view(), name='course-create'),     
    path('courses/<str:course_name>/', CourseCreateView.as_view(), name='course-detail'),  
    path('add_lessons/<str:course_name>/', AddCourseLessonView.as_view(), name='add_course_lesson'),  
    path('courses/update/<str:course_name>/', CourseUpdateView.as_view(), name='course-update'),
    path('programs/', ProgramCreateAPIView.as_view(), name='program-list-create'),
    path('programs/<str:name>/', ProgramRetrieveUpdateDestroyAPIView.as_view(), name='program-retrieve-update-destroy'),
]