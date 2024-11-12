from django.db import models
from cloudinary.models import CloudinaryField
from cloudinary.uploader import destroy
from courses.models import Batch

class VideoChunks(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    video_chunk = models.FileField(upload_to='video_chunks/', null=False)
    chunk_serial = models.IntegerField()
    uploaded_at = models.DateField(auto_now_add=True)
    record_id = models.CharField(null=True)

class SessionVideos(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    date=models.DateField()
    video = CloudinaryField('video', resource_type='video', folder='Session_videos/',  null=False)
    video_serial = models.IntegerField(default=0)

    def delete(self, *args, **kwargs):
        if self.video and self.video.public_id:
            destroy(self.video.public_id, resource_type='video')        
        super().delete(*args, **kwargs)