from rest_framework import serializers
from .models import VideoChunks, SessionVideos

class VideoChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoChunks
        fields = ['batch', 'video_chunk', 'chunk_serial', 'record_id']

class SessionSerializer(serializers.ModelSerializer):
    video = serializers.FileField(use_url=True)
    
    class Meta:
        model = SessionVideos
        fields = ['batch', 'date', 'video', 'video_serial']