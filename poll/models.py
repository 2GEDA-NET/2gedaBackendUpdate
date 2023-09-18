from django.db import models
from user.models import *


class Option(models.Model):
    content = models.CharField(max_length=250)


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    option = models.ForeignKey(Option, on_delete=models.CASCADE)


POLL_TYPE = (
    ('', ''),
)

POLL_DURATION = (
    ('', ''),
)


class Poll(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.CharField(max_length=250)
    options = models.ForeignKey(Option, on_delete=models.CASCADE)
    # duration = models.TimeField()
    duration = models.CharField(max_length=250, choices = POLL_DURATION)
    type = models.CharField(max_length=250, choices=POLL_TYPE)
    image = models.ImageField(upload_to='poll-media/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

