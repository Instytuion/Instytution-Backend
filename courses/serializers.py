from rest_framework import serializers
from .models import (
    Course,
)

class RetrieveProgramsSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    image = serializers.ImageField(use_url=True, required=True)

class RetrieveLatestCourseSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True, required=True)
    program_name = serializers.SerializerMethodField()
    class Meta:
        model    = Course
        fields   = ['name', 'price', 'program_name', 'duration', 'image']

    def get_program_name(self, obj):
        return obj.program.name if obj.program else None