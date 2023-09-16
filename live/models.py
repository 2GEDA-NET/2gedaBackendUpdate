from django.db import models

class VideoSession(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Video(models.Model):
    title = models.CharField(max_length=255)
    video_file = models.FileField(upload_to='videos/')
    hls_ready = models.BooleanField(default=False)  # Indicates if the video is ready for HLS streaming

    def __str__(self):
        return self.title