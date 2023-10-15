from django.db import models
from core.models import UserModel, Notification, BlockedUser


MESSAGE_STORAGE_CHOICES = [
        ('7 days', '7 days'),
        ('monthly', '1 month'),
        ('never', 'Never'),
        ('forever', 'Forever'),
    ]
class ChatSettings(models.Model):
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE)
    enable_notifications = models.BooleanField(default=True)
    message_storage_duration = models.CharField(
    max_length=10,
    default='forever',  # Set the default to 'forever'
    choices=MESSAGE_STORAGE_CHOICES
)
    blocked_users = models.ManyToManyField(UserModel, related_name='blocked_by_users')

    def __str__(self):
        return f"Chat Settings for {self.user.username}"

    def toggle_notifications(self):
        # Toggle the enable_notifications field between True and False
        self.enable_notifications = not self.enable_notifications
        self.save()
    


