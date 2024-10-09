from django.urls import path
from .views import *


urlpatterns = [
    path('batches/', RetrieveInstructorBatchesView.as_view(), name='instructor_batches'),
]