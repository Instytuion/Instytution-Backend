from .serializers import(
    RetrieveProgramsSerializer,
    RetrieveLatestCourseSerializer,
)
from .models import(
    Program,
    Course,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView

class RetrieveProgramsView(ListAPIView):
    queryset = Program.objects.all()
    serializer_class = RetrieveProgramsSerializer
    permission_classes = [IsAuthenticated]

class RetrieveLatestCourseView(ListAPIView):
    queryset = Course.objects.order_by('-created_at')[:4]
    serializer_class = RetrieveLatestCourseSerializer
    permission_classes = [IsAuthenticated]