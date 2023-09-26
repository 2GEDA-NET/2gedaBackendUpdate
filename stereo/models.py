from django.db import models
from django.contrib.auth.hashers import make_password
from user.models import *
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.files import File
from datetime import timedelta
from pydub import AudioSegment

class StereoAccount(models.Model):
    profile = models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    stereo_username = models.CharField(max_length= 250)
    stereo_password = models.CharField(max_length= 250)
    is_artist = models.BooleanField(default=False)
    is_listener = models.BooleanField(default=True)
    artist_name = models.CharField(max_length=250, blank=True, null=True)

    def set_password(self, password):
        self.stereo_password = make_password(password)


class DownloadRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    song = models.ForeignKey('Song', on_delete=models.CASCADE)
    downloaded_at = models.DateTimeField(auto_now_add=True)

class UserSongPreference(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    song = models.ForeignKey('Song', on_delete=models.CASCADE)
    is_like = models.BooleanField(default=True)  # True for like, False for dislike
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'song']


class Genre(models.Model):
    name = models.CharField(max_length=255)

class Artist(models.Model):
    name = models.CharField(max_length=255)
    about = models.TextField()

class Album(models.Model):
    title = models.CharField(max_length=255)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    release_date = models.DateField()
    is_top_album = models.BooleanField(default=False, blank=True, null=True)

class Song(models.Model):
    title = models.CharField(max_length=255)
    cover_image = models.ImageField(upload_to='cover-images/', default='default-audio.png')
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    audio_file = models.FileField(upload_to='songs/')
    duration = models.DurationField(verbose_name=_('Duration'), blank=True, null=True)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True)
    is_quick_pick = models.BooleanField(default=False, verbose_name='Quick Picks')
    is_top_track = models.BooleanField(default=False, verbose_name='Top Tracks')
    is_big_hit = models.BooleanField(default=False, verbose_name='Big Hit')
    uploaded_at = models.DateField(auto_now_add=True)
    download_count = models.PositiveIntegerField(default=0)
    stream_count = models.PositiveIntegerField(default=0)



    def calculate_audio_duration(self):
        try:
            audio = AudioSegment.from_file(self.audio_file.path)
            duration_seconds = audio.duration_seconds
            return timedelta(seconds=duration_seconds)
        except Exception as e:
            # Handle exceptions (e.g., if the file is not a valid audio file)
            return None

    def save(self, *args, **kwargs):
        # Calculate and set the audio duration before saving the model
        self.duration = self.calculate_audio_duration()
        super(Song, self).save(*args, **kwargs)


class MusicProfile(models.Model):
    user = models.ForeignKey(StereoAccount, on_delete=models.CASCADE)
    favorite_genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True)
    playlists = models.ManyToManyField('Playlist', related_name='users', blank=True)
    listening_history = models.ManyToManyField(Song, related_name='listeners', blank=True)
    playlist_count = models.PositiveIntegerField(default=0)


    def increment_playlist_count(self):
        self.playlist_count += 1
        self.save()

    def decrement_playlist_count(self):
        self.playlist_count -= 1
        self.save()


class Playlist(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(MusicProfile, on_delete=models.CASCADE)
    songs = models.ManyToManyField(Song, related_name='playlists', blank=True)

class Chart(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE)