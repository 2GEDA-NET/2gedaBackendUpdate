from django.db import models
from user.models import *

# Create your models here.
# class Chat(models.Model):
#     message = models.TextField()
#     timestamp = models.DateTimeField(blank = True, null = True)
#     is_read = models.BooleanField(default = False, verbose_name = "Read")
#     is_delivered = models.BooleanField(default = False, verbose_name = "Delivered")

class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    group_name = models.CharField(max_length=255, blank=True, null=True)  # Name of a group conversation
    is_group = models.BooleanField(default=False)  # Indicates if it's a group conversation
    group_members = models.ManyToManyField(User, related_name='group_conversations', blank=True)  # Members of a group conversation
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the conversation was created
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp when the conversation was last updated
    is_archived = models.BooleanField(default=False)  # Indicates if the conversation is archived
    unread_count = models.PositiveIntegerField(default=0)  # Count of unread messages in the conversation

    def __str__(self):
        if self.is_group:
            return self.group_name if self.group_name else f'Group Conversation {self.id}'
        else:
            participants_names = ', '.join([user.username for user in self.participants.all()])
            return f'Conversation ({participants_names})'

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False, verbose_name='Read')
    is_delivered = models.BooleanField(default=False, verbose_name='Deluvered')
    is_private = models.BooleanField(default=False, verbose_name='Private Messages')
    is_public = models.BooleanField(default=False, verbose_name='Public Messages')

