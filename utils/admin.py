from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import DemoSong, Demovideo

# Register your models here.
@admin.register(DemoSong)
class EventCategory(ImportExportModelAdmin):
    list_display = ('title', 'cover_image', 'audio_file')

@admin.register(Demovideo)
class EventCategory(ImportExportModelAdmin):
    list_display = ('title', 'cover_image', 'video_file')
