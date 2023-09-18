from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *

# Register your models here.

@admin.register(VideoSession)
class VideoSessionAdmin(ImportExportModelAdmin):
    list_display = ('title', 'description', 'date_created')

@admin.register(Video)
class VideoAdmin(ImportExportModelAdmin):
    list_display = ('title', 'video_file', 'hls_ready')
