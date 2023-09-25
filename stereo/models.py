from django.db import models
from django.contrib.auth.hashers import make_password
from user.models import *


class StereoAccount(models.Model):
    profile = models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    stereo_username = models.CharField(max_length= 250)
    stereo_password = models.CharField(max_length= 250)
    is_artist = models.BooleanField(default=False)
    is_listener = models.BooleanField(default=True)
    artist_name = models.CharField(max_length=250, blank=True, null=True)

    def set_password(self, password):
        self.stereo_password = make_password(password)

class Genre(models.Model):
    name = models.CharField(max_length=255)

class Artist(models.Model):
    name = models.CharField(max_length=255)

class Album(models.Model):
    title = models.CharField(max_length=255)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    release_date = models.DateField()

class Song(models.Model):
    title = models.CharField(max_length=255)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    audio_file = models.FileField(upload_to='songs/')
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True)

class MusicProfile(models.Model):
    user = models.ForeignKey(StereoAccount, on_delete=models.CASCADE)
    favorite_genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True)
    playlists = models.ManyToManyField('Playlist', related_name='users', blank=True)
    listening_history = models.ManyToManyField(Song, related_name='listeners', blank=True)

class Playlist(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(MusicProfile, on_delete=models.CASCADE)
    songs = models.ManyToManyField(Song, related_name='playlists', blank=True)
