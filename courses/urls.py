from django.urls import path
from .views import *

urlpatterns = [
    path('programs/', RetrieveProgramsView.as_view(), name='retrieve_programs'),
    path('latest_courses/', RetrieveLatestCourseView.as_view(), name='latest_courses'),
    path('programs/<str:program_name>/', RetrieveProgramCoursesView.as_view(), name='courses_per_program'),
    path('course_detail/<str:name>/', RetrieveCourseDetailView.as_view(), name='course_details'),
    path('related_courses/<str:course_name>/', RetrieveRelatedCoursesView.as_view(), name='related_courses'),
    path('course_batches/<str:course_name>/', RetrieveCourseBatchesView.as_view(), name='Course_batches'),
    path('instructors/<str:role>/', ListInstructorsApiView.as_view(), name='List_instructors'),
]