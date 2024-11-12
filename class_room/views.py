from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from courses.models import Batch
from .models import VideoChunks, SessionVideos
from .serializers import VideoChunkSerializer
from django.utils.dateparse import parse_date
from django.db import transaction
from .tasks import video_binding_process

class ReceiveVideoChunks(APIView):
    ''' To stoere video chunks to DB temporarly to bind all together later. '''

    def post(self, request, batch_name, chunk_serial, record_id, *args, **kwargs):
        print('Storing video chunk called...')
        video_file = request.FILES.get('video_chunk')
        try:
            batch = Batch.objects.get(name=batch_name)
        except Batch.DoesNotExist:
            return Response({"error": "Batch not found."}, status=status.HTTP_404_NOT_FOUND)

        data = {
            'batch': batch.id,
            'video_chunk': video_file,
            'chunk_serial': chunk_serial,
            'record_id': record_id,
        }

        serializer = VideoChunkSerializer(data=data)
        if serializer.is_valid():
            try:                
                serializer.save()
                print('Video chunk saved to DB')
                return Response({"status": "Video chunk added to DB"}, status=status.HTTP_201_CREATED)
            except Exception as e:
                print('Error while saving video chunk - ', str(e), serializer.errors)
                return Response({"error": "Failed to save video chunk", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            print('serializer invalid...',serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        


class BindVideoChunks(APIView):
    ''' To bind video chunks and save to DB and delete all small chunks from local storage. '''

    def post(self, request, batch_name, batch_date, record_id, *args, **kwargs):
        video_binding_process.delay(batch_name, batch_date, record_id)
        return Response({"status": f'video making for {batch_name} dated on {batch_date} accepted.'}, status=status.HTTP_202_ACCEPTED)
    
from .serializers import SessionSerializer
class SessionVideosListView(APIView):
    ''' To get session video details by serial. '''
    def get(self, request, batch_name, *args, **kwargs): 
        print('Get session video details called...',batch_name)
        print('Session video details', request.data)
        data = SessionVideos.objects.filter(batch__name=batch_name)
        print('data is  from session video',data)
        serializer = SessionSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class VideoBindingStatus(APIView):
    ''' To get status of video chunks binding to update frontend. '''
    def get(self, request, batch_name, batch_date, *args, **kwargs):
        date_obj = parse_date(batch_date)
        try:
            batch = Batch.objects.get(name=batch_name)
        except Batch.DoesNotExist:
            print("Batch not found inside VideoBindingStatus view...")
            return Response({"status": "Batch not found."}, status=status.HTTP_404_NOT_FOUND)
        if not VideoChunks.objects.filter(batch=batch, uploaded_at=date_obj).exists():
            return Response({"status": 'completed'}, status=status.HTTP_201_CREATED)
        else:
            return Response({"status": 'processing'}, status=status.HTTP_200_OK)