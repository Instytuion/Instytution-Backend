from courses.models import *
from rest_framework import serializers
from rest_framework.serializers import ValidationError


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
    image = serializers.ImageField(use_url=True)
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
    image = serializers.ImageField(use_url=True)
    id = serializers.CharField(required=False)
    class Meta:
        model = LessonImage
        fields = ['id', 'image']


class LessonPDFSerializer(serializers.ModelSerializer):
    pdf = serializers.FileField(use_url=True)
    id = serializers.CharField(required=False)
    class Meta:
        model = LessonPDF
        fields = ['id', 'pdf']


class LessonVideoSerializer(serializers.ModelSerializer):
    video = serializers.FileField(use_url=True)
    id = serializers.CharField(required=False)
    class Meta:
        model = LessonVideo
        fields = ['id', 'video']

    def validate_video(self, value):
        if not value.name.endswith(('.mp4', '.mov', '.avi')):
            raise serializers.ValidationError("Invalid video format.")
        return value


class LessonSerializer(serializers.ModelSerializer):
    images = LessonImageSerializer(many=True)
    pdfs = LessonPDFSerializer(many=True)
    videos = LessonVideoSerializer(many=True)
    id = serializers.CharField(read_only=True)
    
    class Meta:
        model = Lesson
        fields = ['id','name', 'description', 'week', 'course', 'images', 'pdfs', 'videos']

    def create(self, validated_data):
        print('inside create method for course lesson - ')
        request = self.context.get('request')
        validated_data['created_by'] = request.user
        validated_data['updated_by'] = request.user

        images_data = validated_data.pop('images')
        pdfs_data = validated_data.pop('pdfs')
        videos_data = validated_data.pop('videos')
        course = validated_data.pop('course')

        lesson = Lesson.objects.create(course=course, **validated_data)

        for image_data in images_data:
            
            LessonImage.objects.create(
                created_by=request.user, updated_by=request.user, lesson=lesson, **image_data
            )

        for pdf_data in pdfs_data:
            LessonPDF.objects.create(
                created_by=request.user, updated_by=request.user, lesson=lesson, **pdf_data
            )

        for video_data in videos_data:
            LessonVideo.objects.create(
            created_by=request.user, updated_by=request.user, lesson=lesson, **video_data
        )


        return lesson

    def update(self, instance, validated_data):
        try:
            print('inside update method for course lesson - ')
            request = self.context.get('request')
            
            instance.description = validated_data.get('description', instance.description)
            instance.week = validated_data.get('week', instance.week)
            instance.updated_by = request.user
            instance.save()

            images_data = validated_data.get('images', [])
            pdfs_data = validated_data.get('pdfs', [])
            videos_data = validated_data.get('videos', [])

            if images_data:
                self._update_related_media(images_data, instance, LessonImage, request)
            if pdfs_data:
                self._update_related_media(pdfs_data, instance, LessonPDF, request)
            if videos_data:
                self._update_related_media(videos_data, instance, LessonVideo, request)

            return instance
        except ValidationError as e:
            print('lesson update ValidationError -', str(e))

    
    def _update_related_media(self, media_data, lesson_instance, MediaModel, request):
        """Helper method to update related media."""
        existing_media_ids = (
            [media.id for media in lesson_instance.images.all()] if MediaModel == LessonImage 
            else [media.id for media in lesson_instance.pdfs.all()] if MediaModel == LessonPDF 
            else [media.id for media in lesson_instance.videos.all()]
            )

        for media in media_data:
            if 'id' in media and int(media['id']) in existing_media_ids:
                print("id found for update media")
                media_instance = MediaModel.objects.get(id=media['id'])
                for attr, value in media.items():
                    if attr != 'id':  # Avoid overwriting the ID
                        setattr(media_instance, attr, value)
                media_instance.updated_by = request.user
                media_instance.save()
            else:
                print("no id found to update media. so creating new media.")
                MediaModel.objects.create(
                    created_by=request.user,
                    updated_by=request.user,
                    lesson=lesson_instance,
                    **media
                )