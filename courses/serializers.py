from rest_framework import serializers
from .models import (
    Course,
)

class RetrieveProgramsSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    image = serializers.ImageField(use_url=True, required=True)

class RetrieveCourseSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True, required=True)
    program_name = serializers.SerializerMethodField(read_only = True)
    week_descriptions = serializers.SerializerMethodField(read_only = True)
    class Meta:
        model    = Course
        fields = ['name', 'price', 'program_name', 'duration', 'image', 'week_descriptions']

    def get_program_name(self, obj):
        return self.context.get('program_name',None)
    
    def get_week_descriptions(self, obj):
        week_descriptions = self.context.get('week_descriptions', [])
        return [{'week': wd.week, 'description': wd.description} for wd in week_descriptions]
    