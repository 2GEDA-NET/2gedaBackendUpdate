from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *

# Register your models here.

@admin.register(Post)
class PostAdmin(ImportExportModelAdmin):
    list_display = ('user', 'content', 'timestamp', 'comments', 'is_business_post', 'is_personal_post')

@admin.register(Comment)
class CommentAdmin(ImportExportModelAdmin):
    list_display = ('user', 'post', 'content', 'reaction', 'timestamp')

@admin.register(Reply)
class ReplyAdmin(ImportExportModelAdmin):
    list_display = ('user', 'comment', 'content', 'reaction')


@admin.register(Reaction)
class ReactionAdmin(ImportExportModelAdmin):
    list_display = ('reaction_type',)

@admin.register(Repost)
class RepostAdmin(ImportExportModelAdmin):
    list_display = ('user', 'content', 'post', 'timestamp', 'reaction', 'comments')

@admin.register(SavedPost)
class SavedPostAdmin(ImportExportModelAdmin):
    list_display = ('user', 'post', 'timestamp')
    