from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from courses.models import Batch
from .models import VideoChunks, SessionVideos
from .serializers import VideoChunkSerializer
from django.utils.dateparse import parse_date
from django.db import transaction
import ffmpeg
from django.core.files import File
import os
from cloudinary.uploader import upload

class ReceiveVideoChunks(APIView):
    ''' To stoere video chunks to DB temporarly to bind all together later. '''

    def post(self, request, batch_name, chunk_serial, *args, **kwargs):
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
        }

        serializer = VideoChunkSerializer(data=data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
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

    @transaction.atomic
    def post(self, request, batch_name, batch_date, *args, **kwargs):
        print('BindVideoChunks post called...')
        date_obj = parse_date(batch_date)
        try:
            batch = Batch.objects.get(name=batch_name)
        except Batch.DoesNotExist:
            print("Batch not found...")
            return Response({"error": "Batch not found."}, status=status.HTTP_404_NOT_FOUND)
        
        video_chunks = VideoChunks.objects.filter(batch=batch, uploaded_at=date_obj).order_by('chunk_serial')
        if not video_chunks.exists():
            print('No video chunks found...')
            return Response({"status": "No video chunks found for the specified batch and date."}, status=status.HTTP_404_NOT_FOUND)
        
        input_files = [chunk.video_chunk.path for chunk in video_chunks]
        output_dir = os.path.dirname(input_files[0])  # Get the directory of the chunk
        if not output_dir:
            print('output_dir not found...')
        output_path = os.path.join(output_dir, f'session_video_{batch_name}_{batch_date}.webm')

        try:
            # FFmpeg to concatenate videos
            print("Starting video concatenation...")
            ffmpeg.input('concat:' + '|'.join(input_files)) \
            .output(output_path, vcodec='libvpx-vp9', acodec='libopus', threads=1, crf=28, audio_bitrate='64k') \
            .run()
        except Exception as e:
            print(f"FFmpeg concatenation failed: {str(e)}")
            return Response({"error": f"Failed to concatenate video chunks: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        session_videos = SessionVideos.objects.filter(batch=batch, date=date_obj)
        session_video_serials = [session.video_serial for session in session_videos if session.batch == batch and session.date == date_obj]
        next_serial = max(session_video_serials) + 1 if session_video_serials else 1

        try:
            print("Uploading concatenated video to Cloudinary...")
            upload_result = upload(
                output_path,
                resource_type="video",
                folder="Session_videos/"
            )
            print("Creating sessionVideo instance...")
            new_session_video = SessionVideos.objects.create(
                batch=batch,
                date=date_obj,
                video=upload_result['public_id'],
                video_serial=next_serial
            )
            os.remove(output_path)
        except Exception as e:
            print(f"Failed to save session video: {str(e)}")
            return Response({"error": f"Failed to save session video: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        try:
            for chunk in video_chunks:
                chunk.video_chunk.delete(save=False)  # deleting video file without saving DB
                chunk.delete()
            print('video chunks and local video files deleted successfully')
        except Exception as e:
            print('Error while deleteing video chunks -', str(e))
            return Response({"error": "Failed to delete video chunks", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"status": f'session_video_{batch_name}_{batch_date}.webm created successfully.'}, status=status.HTTP_201_CREATED)
    
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