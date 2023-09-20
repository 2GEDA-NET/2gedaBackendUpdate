from django.db.models import Q
from django.db import models
from user.models import *
from django.contrib.auth.models import Group

# Create your models here.
# class Chat(models.Model):
#     message = models.TextField()
#     timestamp = models.DateTimeField(blank = True, null = True)
#     is_read = models.BooleanField(default = False, verbose_name = "Read")
#     is_delivered = models.BooleanField(default = False, verbose_name = "Delivered")

class ThreadManager(models.Manager):
    def by_user(self, **kwargs):
        user = kwargs.get('user')
        lookup = Q(first_person=user) | Q(second_person=user)
        qs = self.get_queryset().filter(lookup).distinct()
        return qs


class Thread(models.Model):
    first_person = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='thread_first_person')
    second_person = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                                     related_name='thread_second_person')
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = ThreadManager()
    class Meta:
        unique_together = ['first_person', 'second_person']


class ChatMessage(models.Model):
    thread = models.ForeignKey(Thread, null=True, blank=True, on_delete=models.CASCADE, related_name='chatmessage_thread')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False, verbose_name='Read')
    is_delivered = models.BooleanField(default=False, verbose_name='Deluvered')
    is_private = models.BooleanField(default=False, verbose_name='Private Messages')
    is_public = models.BooleanField(default=False, verbose_name='Public Messages')


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

# class Message(models.Model):
#     conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
#     sender = models.ForeignKey(User, on_delete=models.CASCADE)
#     content = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)
#     is_read = models.BooleanField(default=False, verbose_name='Read')
#     is_delivered = models.BooleanField(default=False, verbose_name='Deluvered')
#     is_private = models.BooleanField(default=False, verbose_name='Private Messages')
#     is_public = models.BooleanField(default=False, verbose_name='Public Messages')


class Participant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active_friends = models.BooleanField(default=True)
    last_seen = models.TimeField()
    sticking_to = models.ForeignKey('user.UserProfile', on_delete=models.CASCADE, related_name='chats', null=True, blank=True)

    def __str__(self):
        return self.user.username


class ChatGroup(Group):
    """ extend Group model to add extra info"""
    description = models.TextField(blank=True, help_text="description of the group")
    mute_notifications = models.BooleanField(default=False, help_text="disable notification if true")
    icon = models.ImageField(help_text="Group icon", blank=True, upload_to="chartgroupimg/")
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('chat:room', args=[str(self.id)])


class LifeStyle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='status_images/', blank=True, null=True)
    video = models.FileField(upload_to='status_videos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Lifestyle by {self.user.username}"