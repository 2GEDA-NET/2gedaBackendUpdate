from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *


# Register your models here.

@admin.register(Option)
class OptionAdmin(ImportExportModelAdmin):
    list_display = ('content',)

@admin.register(Poll)
class PollAdmin(ImportExportModelAdmin):
    list_display = ('user', 'question', 'options', 'duration', 'type',)


@admin.register(Vote)
class VoteAdmin(ImportExportModelAdmin):
    list_display = ('user', 'option')