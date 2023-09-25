from django.db import models
from datetime import datetime, timedelta
from user.models import *


class Option(models.Model):
    content = models.CharField(max_length=250)


class PollMedia(models.Model):
    image = models.ImageField(upload_to='poll-images/')


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    option = models.ForeignKey(Option, on_delete=models.CASCADE)


POLL_TYPE = (
    ('Private', 'Private'),
    ('Public', 'Public'),
)

# Define the choices for the 'duration' field
POLL_DURATION_CHOICES = [
    ('24 hours', '24 Hours'),
    ('3 days', '3 Days'),
    ('7 days', '7 Days'),
    ('14 days', '14 Days'),
    ('30 days', '30 Days'),
    # Add more choices as needed
]

class Poll(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.CharField(max_length=250)
    options = models.ForeignKey(Option, on_delete=models.CASCADE)
    
    # Use the 'duration' field with choices
    duration = models.CharField(max_length=250, choices=POLL_DURATION_CHOICES)
    
    type = models.CharField(max_length=250, choices=POLL_TYPE)
    image = models.ImageField(upload_to='poll-media/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name='Active')
    is_ended = models.BooleanField(default=False, verbose_name='Ended')

    media = models.ForeignKey(PollMedia, on_delete=models.SET_NULL)

    # Add a field to store the actual end time of the poll
    end_time = models.DateTimeField(null=True, blank=True)

    def set_end_time(self):
        """
        Calculate and set the end time based on the duration.
        """
        if self.duration:
            duration_parts = self.duration.split()
            if len(duration_parts) == 2:
                quantity, unit = int(duration_parts[0]), duration_parts[1].lower()
                if unit == "hour":
                    self.end_time = self.created_at + timedelta(hours=quantity)
                elif unit == "day":
                    self.end_time = self.created_at + timedelta(days=quantity)
                else:
                    raise ValueError("Invalid duration unit. Use 'hour' or 'day'.")
            else:
                raise ValueError("Invalid duration format. Use 'X hour(s)' or 'X day(s)'.")
        else:
            raise ValueError("Duration is required.")

    