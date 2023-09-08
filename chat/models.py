from django.db import models

# Create your models here.
class Chat(models.Model):
    message = models.TextField()
    timestamp = models.DateTimeField(blank = True, null = True)
    is_read = models.BooleanField(default = False, verbose_name = "Read")
    is_delivered = models.BooleanField(default = False, verbose_name = "Delivered")



