from courses.models import *
from rest_framework import serializers


class CourseSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True, required=True)
    program = serializers.CharField(source='program.name')

    class Meta:
        model = Course
        fields = ['id','name', 'price', 'program', 'duration', 'image', 'description', 'skill', 'prerequisite', 'course_level']

    def create(self, validated_data):

        program_name = validated_data.pop('program')['name']

        print('program_name', program_name)

        try:            
            program = Program.objects.get(name=program_name)
        except Program.DoesNotExist:
            raise serializers.ValidationError({"program": "The provided program does not exist."})

        course = Course.objects.create(program=program, **validated_data)
            
        return course
