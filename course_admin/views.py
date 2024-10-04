from rest_framework import status ,generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from accounts.permissions import IsCourseAdmin
from courses.models import Course
from urllib.parse import unquote
from rest_framework.serializers import ValidationError
from django.shortcuts import get_object_or_404
from courses.models import Program
from .serializers import *
from django.db import transaction
from .utils import restructure_lessons_data, restructure_update_lesson_data

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

class AddCourseLessonView(APIView):
    """To add or update Lesson instance of a particular Course"""
    permission_classes = [IsCourseAdmin]

    @transaction.atomic
    def post(self, request, course_name, *args, **kwargs):
        lessons_data = restructure_lessons_data(request.data)
        course = Course.objects.get(name__iexact=course_name)

        for lesson_data in lessons_data:
            lesson_data['name'] = lesson_data.pop('lessonName', None)
            lesson_data['description'] = lesson_data.pop('lessonDescription', None)
            lesson_data['course'] = course.id 

            if 'week' in lesson_data:
                lesson_data['week'] = int(lesson_data['week'])

            serializer = LessonSerializer(data=lesson_data, context={'request': request})

            if serializer.is_valid():
                try:
                    serializer.save()
                    return Response({"status": "lessons created"}, status=status.HTTP_201_CREATED)
                except Exception as e:
                    print('Error while creating Lesson instance - ', str(e))
                    print('Errors serializer:', serializer.errors)
                    return Response({"message":str(e)}, status=status.HTTP_400_BAD_REQUEST)
            else:
                print('LessonSerializer data not valid error inside AddCourseLessonView')
                print('Errors:', serializer.errors)
                return Response({"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    
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
    
class ProgramCreateAPIView(generics.CreateAPIView):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    permission_classes = [IsCourseAdmin]

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user
        )

class ProgramRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    lookup_field = 'name'   

class ListCourseLessonsView(ListAPIView):
    """Fetch all lessons with media for a specific course"""
    serializer_class = LessonSerializer
    permission_classes = [IsCourseAdmin]

    def get_queryset(self):
        course_name = self.kwargs.get('course_name')
        course = get_object_or_404(Course, name__iexact=course_name)
        return Lesson.objects.filter(course=course)
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'status': 'success',
            'message': 'Lessons retrieved successfully.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
class LessonDeleteView(generics.DestroyAPIView):
    """To delete a lesson instanse"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsCourseAdmin]

class LessonUpdateView(APIView):
    """To update a lesson instance along with its related media."""
    permission_classes = [IsCourseAdmin]

    @transaction.atomic
    def patch(self, request, pk, *args, **kwargs):
        try:
            lesson = Lesson.objects.get(pk=pk)
        except Lesson.DoesNotExist:
            raise NotFound(detail="Lesson not found.")
        lessons_data = restructure_update_lesson_data(request.data)

        serializer = LessonSerializer(lesson, data=lessons_data, context={'request': request}, partial=True)
        if serializer.is_valid():
            print('inside valid serializer for lesson update')
            updated_lesson = serializer.save()

            updated_serializer = LessonSerializer(updated_lesson)
            data = {
                "status": "lesson updated",
                "data": updated_serializer.data 
            }
            return Response(data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LessonImageDeleteView(generics.DestroyAPIView):
    """To delete a lesson image"""
    queryset = LessonImage.objects.all()
    serializer_class = LessonImageSerializer
    permission_classes = [IsCourseAdmin]

class LessonVideoDeleteView(generics.DestroyAPIView):
    """To delete a lesson video"""
    queryset = LessonVideo.objects.all()
    serializer_class = LessonVideoSerializer
    permission_classes = [IsCourseAdmin]

class LessonPdfDeleteView(generics.DestroyAPIView):
    """To delete a lesson pdf"""
    queryset = LessonPDF.objects.all()
    serializer_class = LessonPDFSerializer
    permission_classes = [IsCourseAdmin]

class LessonImageCreateView(generics.CreateAPIView):
    """To create an instance of a lesson image"""
    queryset = LessonImage.objects.all()
    serializer_class = LessonImageSerializer
    permission_classes = [IsCourseAdmin]

    def perform_create(self, serializer):
        lesson = Lesson.objects.get(id=self.request.data.get('lesson'))
        serializer.save(
            lesson=lesson,
            created_by=self.request.user,
            updated_by=self.request.user
        )


class ListCreateBatchView(generics.ListCreateAPIView):
    permission_classes = [IsCourseAdmin]
    serializer_class = BatchSerializer

    def get_queryset(self):
        course_name = self.kwargs['course_name']        
        queryset = Batch.objects.filter(course__name__iexact=course_name)
        return queryset

class RetrieveUpdateBatchView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsCourseAdmin]  
    serializer_class = BatchSerializer

    def get_queryset(self):
        return Batch.objects.filter(id=self.kwargs['pk'])
    
class LessonPdfCreateView(generics.CreateAPIView):
    """To create an instance of a lesson pdf"""
    queryset = LessonPDF.objects.all()
    serializer_class = LessonPDFSerializer
    permission_classes = [IsCourseAdmin]

    def perform_create(self, serializer):
        lesson = Lesson.objects.get(id=self.request.data.get('lesson'))
        serializer.save(
            lesson=lesson,
            created_by=self.request.user,
            updated_by=self.request.user
        )
