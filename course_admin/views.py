from rest_framework import status ,generics
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import CourseSerializer
from accounts.permissions import IsCourseAdmin
from courses.models import Course
from urllib.parse import unquote
from rest_framework.serializers import ValidationError
from django.shortcuts import get_object_or_404

class CourseCreateView(APIView):
    """ api for create new course and return its data """
    permission_classes = [IsCourseAdmin]

    def get(self, request, *args, **kwargs):
        course_name = unquote(kwargs.get('course_name', None))  
        if course_name: 
            try:
                course = Course.objects.get(name=course_name)
                serializer = CourseSerializer(course)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Course.DoesNotExist:
                return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, *args, **kwargs):
        print('request data',request.data)
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(created_by=request.user, updated_by=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CourseUpdateView(generics.UpdateAPIView):
    """ API for updating an existing course """
    permission_classes = [IsCourseAdmin]
    serializer_class = CourseSerializer

    def get_object(self):
        """ Retrieve the course instance to be updated. """
        course_name = self.kwargs.get('course_name', None)
        if course_name:
            return get_object_or_404(Course, name=unquote(course_name))
        raise ValidationError({"course_name": "Course name is required."})

    def patch(self, request, *args, **kwargs):
        course = self.get_object()
        serializer = self.get_serializer(course, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)