from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *

# Register your models here.

# @admin.register(Thread)
# class ThreadAdmin(ImportExportModelAdmin):
#     list_display = ('first_person', 'second_person', 'updated', 'timestamp',)

@admin.register(Conversation)
class ConversationAdmin(ImportExportModelAdmin):
    list_display = ('get_participant_names', 'group_name', 'is_group', 'get_group_member_names', 'updated_at', 'created_at', 'is_archived', 'unread_count')

    def get_participant_names(self, obj):
        return ", ".join([str(participant) for participant in obj.participants.all()])
    get_participant_names.short_description = 'Participants'

    def get_group_member_names(self, obj):
        return ", ".join([str(member) for member in obj.group_members.all()])
    get_group_member_names.short_description = 'Group Members'

# @admin.register(Message)
# class MessageAdmin(ImportExportModelAdmin):
#     list_display = ('conversation', 'sender', 'content', 'timestamp', 'is_read', 'is_delivered', 'is_private', 'is_public')

@admin.register(BroadcastPlan)
class BroadcastPlanAdmin(ImportExportModelAdmin):
    list_display = ('name', 'description', 'price')

@admin.register(BroadcastPermission)
class BroadPermissionAdmin(ImportExportModelAdmin):
    list_display = ('user', 'remaining_recipients')

@admin.register(ChatGroup)
class ChatGroupAdmin(ImportExportModelAdmin):
    """ enable Chart Group admin """
    list_display = ('id', 'name', 'description', 'icon', 'mute_notifications', 'date_created', 'date_modified')
    list_filter = ('id', 'name', 'description', 'icon', 'mute_notifications', 'date_created', 'date_modified')
    list_display_links = ('name',)


admin.site.register(ChatMessage)


class ChatMessage(admin.TabularInline):
    model = ChatMessage



class ThreadAdmin(admin.ModelAdmin):
    inlines = [ChatMessage]
    class Meta:
        model = Thread


admin.site.register(Thread, ThreadAdmin)