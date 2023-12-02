from collections.abc import Iterable
from django.db import models
from datetime import datetime, timedelta
from user.models import *
from django.utils import timezone
import uuid
from user.models import UserProfile

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_reference = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, default='pending')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment by {self.user.username} - ₦{self.amount}"


class Option(models.Model):
    content = models.CharField(max_length=250)


class Option_List(models.Model):
    content = models.CharField(max_length=250)
    option_image = models.ImageField(upload_to='poll-images/')
    all_vote = models.IntegerField(default=0)
    votee = models.ManyToManyField(User, related_name="Each_Voter")
    

    def save(self,*args, **kwargs ) -> None:
        return super().save(*args, **kwargs)


class PollMedia(models.Model):
    image = models.ImageField(upload_to='poll-images/')


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    # poll = models.ForeignKey('Poll', related_name="each_poll",  on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    cost = models.DecimalField(max_digits=10, null=True, decimal_places=2) 
    # have_Voted = models.BooleanField(default=False)
    # vote_id = models.UUIDField(default=uuid.uuid4())
    all_poll = models.ForeignKey('Poll', related_name="each_poll",  on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"Vote by {self.user.username} on poll: {self.poll.question}"
    

class Voting(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    poll = models.ForeignKey('Poll', related_name="get_poll",  on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    cost = models.DecimalField(max_digits=10, null=True, decimal_places=2) 
    have_Voted = models.BooleanField(default=False)
    vote_id = models.UUIDField(null=True)
    

    def __str__(self):
        return f"Vote by {self.user.username} on poll: {self.poll.question}"
    


# Define the choices for the 'type' field
POLL_PRIVACY = (
    ('Private', 'Private'),
    ('Public', 'Public'),
)

POLL_TYPE = (
    ('Free', 'Free'),
    ('Paid', 'Paid'),
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    question = models.CharField(max_length=250)
    options = models.ManyToManyField(Option, related_name="pollsoption")
    
    # Use the 'duration' field with choices
    duration = models.CharField(max_length=250, choices=POLL_DURATION_CHOICES)
    
    type = models.CharField(max_length=250, choices=POLL_TYPE, default="Free")
    privacy = models.CharField(max_length=250, choices=POLL_PRIVACY, default="Public")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name='Active')
    is_ended = models.BooleanField(default=False, verbose_name='Ended')

    media = models.ForeignKey(PollMedia, on_delete=models.SET_NULL, null=True)
    access_requests = models.ManyToManyField(User, related_name='requested_polls', blank=True)

    end_time = models.DateTimeField(null=True, blank=True)
    access_requests = models.ManyToManyField(User, related_name='requested_polls', blank=True)
    options_list = models.ManyToManyField(Option_List, related_name='optionnewlist')
    vote_count = models.PositiveIntegerField(default=0)
    vote_id = models.UUIDField(
        default=uuid.uuid4, editable=False
    )
    is_editable = models.BooleanField(default=False)
    user_profile = models.ForeignKey(UserProfile, related_name="user_profile_polls", on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=250, null=True)
    time_stamp = models.DateTimeField(default=timezone.now)
    
    
    

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

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'poll')

CURRENCY = (
    ("USD","USD"),
    ("NGN", "NGN")
)


class Instatiate_Payment(models.Model):
    polls = models.ForeignKey(Poll, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    amount = models.IntegerField(null=True)
    payment_type = models.CharField(choices=CURRENCY, max_length=200, default="NGN")
    url = models.CharField(max_length=256, null=True)
    is_instantiated = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    ref_no = models.CharField(null=True)





