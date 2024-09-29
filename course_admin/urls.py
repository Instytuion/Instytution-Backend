from django.urls import path
from .views import CourseCreateView, AddCourseLessonView

urlpatterns = [
    path('courses/', CourseCreateView.as_view(), name='course-create'),     
    path('courses/<str:course_name>/', CourseCreateView.as_view(), name='course-detail'),  
    path('add_lessons/<str:course_name>/', AddCourseLessonView.as_view(), name='add_course_lesson'),  
]