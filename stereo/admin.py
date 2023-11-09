from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *

# Register your models here.

@admin.register(Genre)
class GenreAdmin(ImportExportModelAdmin):
    list_display = ('name',)

@admin.register(Song)
class SongAdmin(ImportExportModelAdmin):
    list_display = ('title', 'album', 'audio_file', 'genre')

@admin.register(MusicProfile)
class MusicProfileAdmin(ImportExportModelAdmin):
    list_display = ('user', 'favorite_genre', 'listening_history_summary')
    
    def listening_history_summary(self, obj):
        return obj.listening_history.count()  # Assuming you want to display the count of listened songs
    
    listening_history_summary.short_description = 'Listening History Summary'


@admin.register(Playlist)
class PlaylistAdmin(ImportExportModelAdmin):
    list_display = ('name', 'user', 'get_song_count')

    def get_song_count(self, obj):
        return obj.songs.count()
    
    get_song_count.short_description = 'Number of Songs'