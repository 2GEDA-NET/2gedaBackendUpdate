from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *
# Register your models here.


@admin.register(ConnectPost)
class ConnectPostAdmin(ImportExportModelAdmin):
    list_display = ('user', 'text', 'created_at')
