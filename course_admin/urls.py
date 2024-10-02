from django.urls import path
from .views import *

urlpatterns = [
    path('courses/', CourseCreateView.as_view(), name='course-create'),     
    path('courses/<str:course_name>/', CourseCreateView.as_view(), name='course-detail'),  
    path('add_lessons/<str:course_name>/', AddCourseLessonView.as_view(), name='add_course_lesson'),  
    path('courses/update/<str:course_name>/', CourseUpdateView.as_view(), name='course-update'),
    path('programs/', ProgramCreateAPIView.as_view(), name='program-list-create'),
    path('program/<str:name>/', ProgramRetrieveUpdateDestroyAPIView.as_view(), name='program-retrieve-update-destroy'),
    path('lessons/<str:course_name>/', ListCourseLessonsView.as_view(), name='list-course-lessons'),
    path('delete_lesson/<int:pk>/', LessonDeleteView.as_view(), name='delete_lesson'),
    path('update_lesson/<int:pk>/', LessonUpdateView.as_view(), name='update_lesson'),
    path('delete_lesson_image/<int:pk>/', LessonImageDeleteView.as_view(), name='delete_lesson_image'),
    path('delete_lesson_video/<int:pk>/', LessonVideoDeleteView.as_view(), name='delete_lesson_video'),
    path('delete_lesson_pdf/<int:pk>/', LessonPdfDeleteView.as_view(), name='delete_lesson_pdf'),
]