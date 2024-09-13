from django.urls import path
from .views import *

urlpatterns = [
    path('programs/', RetrieveProgramsView.as_view(), name='retrieve_programs'),
]