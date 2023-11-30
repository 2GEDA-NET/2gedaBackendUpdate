from django.db import models
from storages.backends.s3boto3 import S3Boto3Storage
from utils.Customstorage import CustomS3Boto3Storage
from django.utils.translation import gettext_noop as _
from user.models import User


# Create your models here.
class DemoSong(models.Model):
    title = models.CharField(max_length=255)
    cover_image = models.ImageField(upload_to='cover-images/')
    audio_file = models.FileField(upload_to='songs/', storage=CustomS3Boto3Storage())


class Demovideo(models.Model):
    title = models.CharField(max_length=255)
    cover_image = models.ImageField(upload_to='cover-images/', default='default-audio.png')
    video_file = models.FileField(upload_to='video/', storage=CustomS3Boto3Storage())

    def __str__(self) -> str:
        return super().__str__()


class Geopraphical_Location(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    description = models.CharField(_(""), max_length=50, null=True)
    platform = models.CharField(_(""), max_length=50, null=True)
    websiteurl = models.CharField(_(""), max_length=50, null=True)
    location = models.CharField(_(""), max_length=50, null=True)
    address = models.CharField(_(""), max_length=50, null=True)
    ticket_name = models.CharField(_(""), max_length=50, null=True)
    category = models.CharField(_(""), max_length=50, null=True)
    fee_settings_category = models.CharField(_(""), max_length=50, null=True)
    quantity = models.CharField(_(""), max_length=50, null=True)
    price = models.CharField(_(""), max_length=50, null=True)
    IsPrivate = models.CharField(_(""), max_length=50, null=True)
    IsPublic = models.CharField(_(""), max_length=50, null=True)
    show_remaining_ticket = models.CharField(_(""), max_length=50, null=True)
    X_File = models.FileField(upload_to="loacation", null=True)
