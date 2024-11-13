from django.urls import path
from .views import *

urlpatterns = [
    path('video-chunks/<str:batch_name>/<int:chunk_serial>/<str:record_id>/',ReceiveVideoChunks.as_view() , name='video_chunks'),
    path('bind-video-chunks/<str:batch_name>/<str:batch_date>/<str:record_id>/',BindVideoChunks.as_view() , name='bind_video_chunks'),
    path('get-video/<str:batch_name>/',SessionVideosListView.as_view() , name='get_session_videos'),
    path('bind-video-status/<str:batch_name>/<str:batch_date>/',VideoBindingStatus.as_view() , name='bind_video_status'),

]