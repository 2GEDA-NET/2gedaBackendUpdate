from django.db import models
from storages.backends.s3boto3 import S3Boto3Storage
from utils.Customstorage import CustomS3Boto3Storage


# Create your models here.
class DemoSong(models.Model):
    title = models.CharField(max_length=255)
    cover_image = models.ImageField(upload_to='cover-images/', default='default-audio.png')
    audio_file = models.FileField(upload_to='songs/', storage=CustomS3Boto3Storage())


class Demovideo(models.Model):
    title = models.CharField(max_length=255)
    cover_image = models.ImageField(upload_to='cover-images/', default='default-audio.png')
    video_file = models.FileField(upload_to='video/', storage=CustomS3Boto3Storage())

    def __str__(self) -> str:
        return super().__str__()


    
    
