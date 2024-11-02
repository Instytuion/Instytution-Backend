from django.urls import path
from .views import *

urlpatterns = [
    path('video-chunks/<str:batch_name>/<int:chunk_serial>/',ReceiveVideoChunks.as_view() , name='video_chunks'),
    path('bind-video-chunks/<str:batch_name>/<str:batch_date>/',BindVideoChunks.as_view() , name='bind_video_chunks'),
    path('get-video/<str:batch_name>/',SessionVideosListView.as_view() , name='get_session_videos'),

]