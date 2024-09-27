from .serializers import(
    RetrieveProgramsSerializer,
    RetrieveCourseSerializer,
    BatchSerializer,
    ProgramSerializer
)
from .models import(
    Program,
    Course,
    CourseWeekDescription,
    Batch
)
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django.utils import timezone
from rest_framework import generics
from accounts.permissions import IsCourseAdmin

class RetrieveLatestCourseView(ListAPIView):
    '''
    to fetch course data of latest 4 courses.
    '''
    queryset = Course.objects.order_by('-created_at')[:4]
    serializer_class = RetrieveCourseSerializer

class RetrieveProgramCoursesView(ListAPIView):
    '''
    to fetch course data as per the specified program name.
    '''
    serializer_class = RetrieveCourseSerializer

    def get_queryset(self):
        
        program_name = self.kwargs['program_name']
        print('program name in url is -', program_name)
        return Course.objects.filter(program__name__iexact=program_name)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['program_name'] = self.kwargs.get('program_name')
        return context
    
class RetrieveCourseDetailView(RetrieveAPIView):
    '''
    to fetch detail data of a specific course by course in the utl.
    '''
    serializer_class = RetrieveCourseSerializer
    lookup_field = 'name'

    def get_queryset(self):
        course_name = self.kwargs['name']
        print(f"Lookup name from URL: {course_name}")
        queryset = Course.objects.filter(name__iexact = course_name)
        return queryset
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        queryset = self.get_queryset().first()
        if queryset:
            week_descriptions = CourseWeekDescription.objects.filter(course=queryset)
            context['week_descriptions'] = week_descriptions
        else:
            print('inside RetrieveCourseDetailView. queryset obj None.')
        return context
    
class RetrieveRelatedCoursesView(ListAPIView):
    '''
    to fetch course data related to the specified course name in the url.
    '''
    serializer_class = RetrieveCourseSerializer

    def get_queryset(self):
        
        course_name = self.kwargs['course_name']
        print('course name in url is -', course_name)
        match_str = course_name.split(' ')[0]
        print('match_str made from url is -', match_str)
        return Course.objects.filter(name__icontains=match_str).exclude(name__iexact=course_name)[:10]
    
class RetrieveCourseBatchesView(ListAPIView):
    serializer_class = BatchSerializer


    def get_queryset(self):
        current_date = timezone.now().date()
        course_name = self.kwargs['course_name']
        print('course name in url is -', course_name)
        return Batch.objects.filter(start_date__gt=current_date,course__name__iexact=course_name)

    
class ProgramListCreateAPIView(generics.ListCreateAPIView):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    permission_classes=[IsCourseAdmin]

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user
        )

class ProgramRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer