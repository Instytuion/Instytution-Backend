from rest_framework import serializers
from .models import VideoChunks

class VideoChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoChunks
        fields = ['batch', 'video_chunk', 'chunk_serial']

