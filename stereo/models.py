from django.db import models
from user.models import *

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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    favorite_genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True)
    playlists = models.ManyToManyField('Playlist', related_name='users', blank=True)
    listening_history = models.ManyToManyField(Song, related_name='listeners', blank=True)

class Playlist(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(MusicProfile, on_delete=models.CASCADE)
    songs = models.ManyToManyField(Song, related_name='playlists', blank=True)
