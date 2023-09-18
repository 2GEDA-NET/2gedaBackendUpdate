from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *

# Register your models here.
@admin.register(Conversation)
class ConversationAdmin(ImportExportModelAdmin):
    list_display = ('get_participant_names', 'group_name', 'is_group', 'get_group_member_names', 'updated_at', 'created_at', 'is_archived', 'unread_count')

    def get_participant_names(self, obj):
        return ", ".join([str(participant) for participant in obj.participants.all()])
    get_participant_names.short_description = 'Participants'

    def get_group_member_names(self, obj):
        return ", ".join([str(member) for member in obj.group_members.all()])
    get_group_member_names.short_description = 'Group Members'

@admin.register(Message)
class MessageAdmin(ImportExportModelAdmin):
    list_display = ('conversation', 'sender', 'content', 'timestamp', 'is_read', 'is_delivered', 'is_private', 'is_public')
