from collections.abc import Iterable
from django.db.models import Q
from django.db import models
from user.models import *
from django.contrib.auth.models import Group
from cryptography.fernet import Fernet
import base64
from channels.db import database_sync_to_async


# Create your models here.

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

# This conversation works like a group chat
class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    group_name = models.CharField(max_length=255, blank=True, null=True)  # Name of a group conversation
    
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
        ('participant', 'Participant'),
    ]

    roles = models.JSONField(default=dict)
    is_group = models.BooleanField(default=False)  # Indicates if it's a group conversation
    group_members = models.ManyToManyField(User, related_name='group_conversations', blank=True)  # Members of a group conversation
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the conversation was created
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp when the conversation was last updated
    is_archived = models.BooleanField(default=False)  # Indicates if the conversation is archived
    unread_count = models.PositiveIntegerField(default=0)  # Count of unread messages in the conversation
    is_deleted = models.BooleanField(default=False)
    # Add a field to store the conversation's encryption key
    encryption_key = models.BinaryField()

    def assign_role(self, user, role):
        """
        Assign a role to a user in the conversation.

        Args:
            user (User): The user to assign the role to.
            role (str): The role to assign (e.g., 'owner', 'participant').

        Returns:
            bool: True if the role was successfully assigned, False otherwise.
        """
        if user.id in self.roles:
            # User already has a role, update it
            self.roles[user.id] = role
        else:
            # User doesn't have a role, add it
            self.roles[user.id] = role
            self.save()
        return True

    def check_role(self, user, role_to_check):
        """
        Check if a user has a specific role in the conversation.

        Args:
            user (User): The user to check.
            role_to_check (str): The role to check (e.g., 'owner', 'participant').

        Returns:
            bool: True if the user has the specified role, False otherwise.
        """
        return self.roles.get(str(user.id)) == role_to_check

    def __str__(self):
        if self.is_group:
            return self.group_name if self.group_name else f'Group Conversation {self.id}'
        else:
            participants_names = ', '.join([user.username for user in self.participants.all()])
            return f'Conversation ({participants_names})'

    @staticmethod
    def generate_encryption_key():
        # Generate a new encryption key for a conversation
        return base64.urlsafe_b64encode(Fernet.generate_key())

    def get_encryption_key(self):
        # Retrieve the conversation's encryption key
        return self.encryption_key

class BroadcastPlan(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class BroadcastPermission(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    max_recipients = models.PositiveIntegerField(default=0)
    remaining_recipients = models.PositiveIntegerField(default=0)



# This conversation works like t
class ChatMessage(models.Model):
    thread = models.ForeignKey(Thread, null=True, blank=True, on_delete=models.CASCADE, related_name='chatmessage_thread')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False, verbose_name='Read')
    is_delivered = models.BooleanField(default=False, verbose_name='Delivered')
    is_private = models.BooleanField(default=False, verbose_name='Private Messages')
    is_public = models.BooleanField(default=False, verbose_name='Public Messages')
    custom_visibility = models.BooleanField(default=False)  # Message-specific visibility flag
    read_only_participants = models.ManyToManyField(User, related_name='read_only_messages', blank=True)
    visible_to = models.ManyToManyField(User, related_name='visible_messages', blank=True)

    # Add fields for encrypted message and IV
    encrypted_message = models.BinaryField()
    iv = models.BinaryField()

    is_reported = models.BooleanField(default=False)  # Flag to indicate if the message is reported
    is_starred = models.BooleanField(default=False)  # Flag to indicate if the message is starred
    is_deleted = models.BooleanField(default=False)
    # Reference to the conversation to which the message belongs
    conversation = models.ForeignKey(Conversation, null=True, blank=True, on_delete=models.CASCADE, related_name='messages')

    is_broadcast = models.BooleanField(default=False, verbose_name='Broadcast Message')
    broadcast_recipients = models.ManyToManyField(User, related_name='received_broadcasts', blank=True)

    @staticmethod
    def encrypt_message(message, encryption_key):
        # Create an encryption cipher with the provided key
        cipher_suite = Fernet(encryption_key)

        # Generate an IV (Initialization Vector)
        iv = Fernet.generate_key()

        # Encrypt the message and IV
        encrypted_message = cipher_suite.encrypt(message.encode())
        return encrypted_message, iv

    @staticmethod
    def decrypt_message(encrypted_message, iv, encryption_key):
        # Create an encryption cipher with the provided key
        cipher_suite = Fernet(encryption_key)

        # Decrypt the message using the IV
        decrypted_message = cipher_suite.decrypt(encrypted_message)
        return decrypted_message.decode()

    @database_sync_to_async
    def create_chat_message(self, thread, user, msg, encryption_key):
        encrypted_message, iv = self.encrypt_message(msg, encryption_key)
        ChatMessage.objects.create(thread=thread, user=user, encrypted_message=encrypted_message, iv=iv)
    
    @database_sync_to_async
    def create_broadcast_message(self, thread, user, msg, encryption_key, recipients):
        encrypted_message, iv = self.encrypt_message(msg, encryption_key)
        message = ChatMessage.objects.create(
            thread=thread,
            user=user,
            encrypted_message=encrypted_message,
            iv=iv,
            is_broadcast=True,  # Set the is_broadcast field to True for broadcast messages
        )
        message.broadcast_recipients.set(recipients)


class Participant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active_friends = models.BooleanField(default=True)
    last_seen = models.TimeField(null=True, blank=True)
    sticking_to = models.ForeignKey('user.UserProfile', on_delete=models.CASCADE, related_name='chats', null=True, blank=True)

    def __str__(self):
        return self.user.username
    
    def save(self, *args, **kwargs) -> None:
        if self.user:
            self.last_seen = self.user.last_seen

        return super().save(*args, **kwargs)


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