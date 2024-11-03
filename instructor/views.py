from django.shortcuts import render
from courses.serializers import BatchSerializer
from courses.models import Batch
from rest_framework.generics import ListAPIView
from .permissions import IsInstructor


class RetrieveInstructorBatchesView(ListAPIView):
    ''' To fetch all batches of an instructor '''

    serializer_class = BatchSerializer
    permission_classes = [IsInstructor]

    def get_queryset(self):
        instructor = self.request.user
        print('instructor is -', instructor)
        return Batch.objects.filter(instructor=instructor)

