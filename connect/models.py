from django.db import models
from user.models import *
# Create your models here.

class ConnectPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    # media = models.FileField(upload_to='connect_media/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ConnectPost by {self.user.username}"