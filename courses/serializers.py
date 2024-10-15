from rest_framework import serializers
from .models import (
    Course,
    Batch,
    BatchStudents,
    Lesson
)
from accounts.models import CustomUser
from course_admin.serializers import LessonSerializer

class RetrieveProgramsSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    image = serializers.ImageField(use_url=True, required=True)

class RetrieveCourseSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True, required=True)
    program_name = serializers.SerializerMethodField(read_only = True)
    week_descriptions = serializers.SerializerMethodField(read_only = True)
    class Meta:
        model = Course
        fields = [
            'name', 'price', 'program_name', 'duration', 'image', 
            'description', 'skill', 'prerequisite', 'week_descriptions', 'course_level'
            ]

    def get_program_name(self, obj):
        return self.context.get('program_name',None)
    
    def get_week_descriptions(self, obj):
        week_descriptions = self.context.get('week_descriptions', [])
        return [{'week': wd.week, 'description': wd.description} for wd in week_descriptions]
    
class BatchSerializer(serializers.ModelSerializer):
    course_name=serializers.CharField(source='course.name', read_only=True)
    instructor_name=serializers.SerializerMethodField()
    student_count = serializers.SerializerMethodField()


    class Meta:
        model = Batch

        fields = [
            'id', 'name', 'course_name', 'instructor_name', 'start_date', 'end_date', 
            'start_time', 'end_time', 'student_count', 'strength'
                  ]

    def get_instructor_name(self, obj):
        first_name = obj.instructor.first_name
        last_name = obj.instructor.last_name

        return f"{first_name} {last_name}"
    
    def get_student_count(self, obj):
        return obj.batch_students.count()
        
class InstructorSerializer(serializers.ModelSerializer):
    instructor_name=serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ['id', 'email' , 'instructor_name', 'profile_picture']

    def get_instructor_name(self, obj):
        first_name = obj.first_name
        last_name = obj.last_name

        return f"{first_name} {last_name}"

class StudentBatchSerializer(serializers.ModelSerializer):
    lesson = serializers.SerializerMethodField()
    batch = BatchSerializer()
    class Meta:
        model = BatchStudents
        fields = ['batch', 'student','lesson']
    def get_lesson(self, obj):
        course = obj.batch.course
        print('course is :', course)
        data = Lesson.objects.filter(course=course)
        print('data is :', data)
        return LessonSerializer(data, many=True).data