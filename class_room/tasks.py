from celery import shared_task
from django.db import transaction
from courses.models import Batch
from .models import VideoChunks, SessionVideos
from django.utils.dateparse import parse_date
import ffmpeg
import os
from cloudinary.uploader import upload

@shared_task
@transaction.atomic
def video_binding_process(batch_name, batch_date):
    print('BindVideoChunks process called...')
    date_obj = parse_date(batch_date)
    
    video_chunks = VideoChunks.objects.filter(batch__name=batch_name, uploaded_at=date_obj).order_by('chunk_serial')
    if not video_chunks.exists():
        print('no video chunks found to process...')
        return None
    
    try:
        batch = Batch.objects.get(name=batch_name)
    except Batch.DoesNotExist:
        print("Batch not found...")
        raise ValueError("Batch not found.")
    
    input_files = [chunk.video_chunk.path for chunk in video_chunks]
    output_dir = os.path.dirname(input_files[0])  # Get the directory of the chunk
    if not output_dir:
        print('output_dir not found...')
        raise ValueError("Output directory for concatenated video not found.")
    
    output_path = os.path.join(output_dir, f'session_video_{batch_name}_{batch_date}.webm')

    try:
        # FFmpeg to concatenate videos
        print("Starting video concatenation...")
        ffmpeg.input('concat:' + '|'.join(input_files)) \
        .output(output_path, vcodec='libvpx-vp9', acodec='libopus', threads=1, crf=28, audio_bitrate='64k') \
        .run()
    except Exception as e:
        print(f"FFmpeg concatenation failed: {str(e)}")
        raise RuntimeError(f"FFmpeg concatenation failed: {str(e)}")

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
        raise RuntimeError(f"Error while uploading to cloudinary and creating session video: {str(e)}")
    
    try:
        for chunk in video_chunks:
            chunk.video_chunk.delete(save=False)  # deleting video file without saving DB
            chunk.delete()
        print('video chunks and local video files deleted successfully')
    except Exception as e:
        print('Error while deleteing video chunks -', str(e))
        raise RuntimeError(f"Error deleting video chunks: {str(e)}")