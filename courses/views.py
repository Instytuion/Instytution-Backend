from .serializers import(
    RetrieveProgramsSerializer,
)
from .models import(
    Program,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView

class RetrieveProgramsView(ListAPIView):
    queryset = Program.objects.all()
    serializer_class = RetrieveProgramsSerializer
    permission_classes = [IsAuthenticated]
