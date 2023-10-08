from django.db import models

from django.contrib.auth.hashers import make_password

from moviepy.video.io.VideoFileClip import VideoFileClip

from core.models import *


# Create your models here.

class TVAccount(models.Model):

    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)

    tv_username = models.CharField(max_length=250)

    tv_password = models.CharField(max_length=250)

    

    def set_password(self, password):

        self.stereo_password = make_password(password)


class VideoCategory(models.Model):

    name = models.CharField(max_length=250)

    desc = models.TextField(blank=True, null= True)


class VideoLike(models.Model):

    user = models.ForeignKey(TVAccount, on_delete=models.CASCADE)

    video = models.ForeignKey('Video', on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)



VISIBILITY_CHOICES = (

    ('Public', 'Public'),

    ('Private', 'Private'),
)


AGE_RANGE_CHOICES = (

    ('All Ages', 'All Ages'),

    ('PG', 'PG (Parental Guidance)'),

    ('13+', '13 and older'),

    ('18+', '18 and older'),

    # Add more age range choices as needed
)


class Video(models.Model):

    title = models.CharField(max_length=250)

    video_file = models.FileField(upload_to='tv-videos/')

    video_cover = models.ImageField(upload_to='video_cover/')

    video_category = models.ForeignKey(VideoCategory, on_delete=models.CASCADE)

    description = models.TextField()

    duration = models.DurationField(verbose_name='Duration', null=True, blank=True)

    date_of_release = models.DateField()

    year_of_release = models.IntegerField()

    visibility = models.CharField(max_length=250, choices=VISIBILITY_CHOICES)

    is_top_movie = models.BooleanField(default=False, verbose_name='Top Movie')

    is_new_release = models.BooleanField(default=False, verbose_name='New Release')

    availbility = models.CharField(max_length=20, choices=AGE_RANGE_CHOICES)

    is_movie_premiere = models.BooleanField(default=False, verbose_name='Movie Premiere')

    download_count = models.PositiveIntegerField(default=0, verbose_name='Download Count')

    hidden = models.BooleanField(default=False)

    scheduled_date_time = models.DateTimeField(null=True, blank=True)
 
    

    def save(self, *args, **kwargs):

        if not self.duration:  # Calculate duration only if it's not already set

            try:

                video_clip = VideoFileClip(self.video_file.path)

                self.duration = video_clip.duration

            except Exception as e:

                # Handle any exceptions that may occur (e.g., invalid video file)

                print(f"Failed to calculate duration: {str(e)}")
        

        super().save(*args, **kwargs)


class Subscription(models.Model):

    user = models.ForeignKey(TVAccount, on_delete=models.CASCADE)

    channel = models.ForeignKey('Channel', on_delete=models.CASCADE)


class Channel(models.Model):

    owner = models.ForeignKey(TVAccount, on_delete=models.CASCADE)

    name = models.CharField(max_length=250)

    description = models.TextField(blank=True, null=True)

    videos = models.ManyToManyField(Video, blank=True)


    def __str__(self):

        return self.name
    

    def subscribers_count(self):

        return Subscription.objects.filter(channel=self).count()


    def is_user_subscribed(self, user):

        return Subscription.objects.filter(user=user, channel=self).exists()


class Comment(models.Model):

    user = models.ForeignKey(TVAccount, on_delete=models.CASCADE)

    video = models.ForeignKey(Video, on_delete=models.CASCADE)

    text = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)


class Like(models.Model):

    user = models.ForeignKey(TVAccount, on_delete=models.CASCADE)

    video = models.ForeignKey(Video, on_delete=models.CASCADE, null=True, blank=True)

    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)

    is_like = models.BooleanField(default=True)  # True for like, False for dislike



class Playlist(models.Model):

    user = models.ForeignKey(TVAccount, on_delete=models.CASCADE)

    name = models.CharField(max_length=250)

    videos = models.ManyToManyField(Video, blank=True)


class Report(models.Model):

    user = models.ForeignKey(TVAccount, on_delete=models.CASCADE)

    video = models.ForeignKey(Video, on_delete=models.CASCADE, null=True, blank=True)

    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)

    reason = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)


class VideoTag(models.Model):

    video = models.ForeignKey(Video, on_delete=models.CASCADE)

    tag = models.CharField(max_length=100)

