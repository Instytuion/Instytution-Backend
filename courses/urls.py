from django.urls import path
from .views import *

urlpatterns = [
    path('programs/', RetrieveProgramsView.as_view(), name='retrieve_programs'),
    path('latest_courses/', RetrieveLatestCourseView.as_view(), name='latest_courses'),
]