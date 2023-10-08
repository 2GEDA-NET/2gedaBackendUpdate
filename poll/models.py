from django.db import models
from datetime import datetime, timedelta
from core.models import *


class Payment(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_reference = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, default='pending')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment by {self.user.username} - ₦{self.amount}"

class Option(models.Model):
    content = models.CharField(max_length=250)


class PollMedia(models.Model):
    image = models.ImageField(upload_to='poll-images/')

class Vote(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    poll = models.ForeignKey('Poll', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)  # Add a cost field for each vote

    def __str__(self):
        return f"Vote by {self.user.username} on poll: {self.poll.question}"


# Define the choices for the 'type' field
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
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    question = models.CharField(max_length=250)
    options = models.ForeignKey(Option, on_delete=models.CASCADE)
    
    # Use the 'duration' field with choices
    duration = models.CharField(max_length=250, choices=POLL_DURATION_CHOICES)
    
    type = models.CharField(max_length=250, choices=POLL_TYPE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name='Active')
    is_ended = models.BooleanField(default=False, verbose_name='Ended')

    media = models.ForeignKey(PollMedia, on_delete=models.SET_NULL, null=True)
    access_requests = models.ManyToManyField(UserModel, related_name='requested_polls', blank=True)
    # Add a field to store the actual end time of the poll
    end_time = models.DateTimeField(null=True, blank=True)

    # Add a field to store the vote count
    vote_count = models.PositiveIntegerField(default=0)

    def count_views(self):
        return PollView.objects.filter(poll=self).count()

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


class PollView(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'poll')