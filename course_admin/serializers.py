from courses.models import *
from rest_framework import serializers
from django.db import transaction


class LessonImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True, required=True)
    class Meta:
        model = LessonImage
        fields = ['name', 'image']

class LessonVideoSerializer(serializers.ModelSerializer):
    video = serializers.FileField(use_url=True, required=True)
    class Meta:
        model = LessonVideo
        fields = ['name', 'video']

class LessonPDFSerializer(serializers.ModelSerializer):
    pdf = serializers.FileField(use_url=True, required=True)
    class Meta:
        model = LessonPDF
        fields = ['name', 'pdf']

class LessonSerializer(serializers.ModelSerializer):
    image = LessonImageSerializer(many=True)
    video = LessonVideoSerializer(many=True)
    chapter = LessonPDFSerializer(many=True)

    class Meta:
        model = Lesson
        fields = ['name', 'week', 'image', 'video', 'chapter']


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
