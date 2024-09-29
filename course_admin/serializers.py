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

        try:            
            program = Program.objects.get(name=program_name)
        except Program.DoesNotExist:
            raise serializers.ValidationError({"program": "The provided program does not exist."})

        course = Course.objects.create(program=program, **validated_data)
            
        return course
    
    def update(self, instance, validated_data):
    
        for attr, value in validated_data.items():
            setattr(instance, attr, value) 
        
        print("Updating instance with:", {attr: getattr(instance, attr) for attr in validated_data})

        instance.updated_by = self.context['request'].user    
        instance.save()
        return instance


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = '__all__'
        read_only_fields = ('created_by', 'updated_by')

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        validated_data['updated_by'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['updated_by'] = self.context['request'].user
        return super().update(instance, validated_data)
    
class LessonImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonImage
        fields = ['image']


class LessonPDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonPDF
        fields = ['pdf']


class LessonVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonVideo
        fields = ['video']

    def validate_video(self, value):
        if not value.name.endswith(('.mp4', '.mov', '.avi')):
            raise serializers.ValidationError("Invalid video format.")
        return value


class LessonSerializer(serializers.ModelSerializer):
    images = LessonImageSerializer(many=True)
    pdfs = LessonPDFSerializer(many=True)
    videos = LessonVideoSerializer(many=True)
    
    class Meta:
        model = Lesson
        fields = ['name', 'description', 'week', 'course', 'images', 'pdfs', 'videos']


    def create(self, validated_data):
        print('inside create lesson data method - ')
        request = self.context.get('request')
        validated_data['created_by'] = request.user
        validated_data['updated_by'] = request.user

        images_data = validated_data.pop('images')
        pdfs_data = validated_data.pop('pdfs')
        videos_data = validated_data.pop('videos')
        course = validated_data.pop('course')

        lesson = Lesson.objects.create(course=course, **validated_data)

        for idx, image_data in enumerate(images_data):
            lesson_name = lesson.name
            name = f'{lesson_name}-img-{idx+1}'
            lesson_image = LessonImage.objects.create(
                created_by=request.user, updated_by=request.user, name=name, **image_data
                )
            lesson.images.add(lesson_image)

        for idx, pdf_data in enumerate(pdfs_data):
            lesson_name = lesson.name
            name = f'{lesson_name}-pdf-{idx+1}'
            lesson_pdf = LessonPDF.objects.create(
                created_by=request.user, updated_by=request.user, name=name, **pdf_data
                )
            lesson.lesson_pdfs.add(lesson_pdf)

        for idx, video_data in enumerate(videos_data):
            lesson_name = lesson.name
            name = f'{lesson_name}-video-{idx+1}'
            try:
                lesson_video = LessonVideo.objects.create(
                    created_by=request.user, updated_by=request.user, name=name, **video_data
                )
                lesson.videos.add(lesson_video)
            except Exception as e:
                print("Error while creating LessonVideo:", e)

        return lesson
