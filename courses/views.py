from .serializers import(
    RetrieveProgramsSerializer,
    RetrieveCourseSerializer,
)
from .models import(
    Program,
    Course,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView

class RetrieveProgramsView(ListAPIView):
    '''
    to fetch all programs.
    '''
    queryset = Program.objects.all()
    serializer_class = RetrieveProgramsSerializer

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
        return Course.objects.filter(program__name__iexact=program_name).select_related('program')