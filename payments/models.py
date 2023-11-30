from collections.abc import Iterable
from django.db import models
from user.models import User
from django.utils import timezone
import uuid
import random

# Create your models here.
SERVICES = (
    ("poll","poll"),
    ("ticket","ticket"),
    ("live","live"),
    ("feed","feed"),
    ("connect","connect"),
    ("commerce","commerce"),
    ("business", "business"),
    ("stereo", "stereo"),
    ("ticket", "ticket"),
    ("tv", "tv"),
)

def create_id():
    num = random.randint(100, 2000)
    num_2 = random.randint(1, 1000)
    num_3 = random.randint(60, 1000)
    return str(num) + str(num_2)+str(num_3)+str(uuid.uuid4())[:8]


class Wallet_Funding(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, editable=False, blank=False, null=True, related_name='wallet_funding')
    medium = models.CharField(max_length=500, blank=True,editable=False, )
    amount = models.IntegerField(editable=False, default=0)
    previous_balance = models.IntegerField(editable=False, default=0 )
    after_balance = models.IntegerField( null=True,editable=False, default=0)
    create_date = models.DateTimeField(default=timezone.now,editable=False, )
    track_id = models.CharField(default=create_id, editable=False, max_length=30)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_prev_balance = self.after_balance
        

    def save(self, *args, **kwargs) -> None:
        if self.amount:
            self.previous_balance = self.init_prev_balance
            self.after_balance = self.init_prev_balance + self.amount
            self.user.account_balance = self.after_balance
            self.user.save()

            Wallet_summary.objects.create(
                    user=self.user, 
                    product="funding", 
                    amount=self.amount, 
                    previous_balance = self.init_prev_balance,
                    after_balance = self.after_balance
                    )
                
            
        return super().save(*args, **kwargs)


class Wallet_summary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             editable=False, blank=False, null=True, related_name='wallet')
    product = models.CharField(max_length=500, blank=True, choices=SERVICES)
    amount = models.IntegerField(default=0, editable=False)
    previous_balance = models.IntegerField(default=0)
    after_balance = models.IntegerField(default=0)
    create_date = models.DateTimeField(default=timezone.now)
    ident = models.CharField(default=create_id, editable=False, max_length=30)

    def __str__(self):
        return str(self.user)

    def save(self, *args, **kwargs):
        
        super(Wallet_summary, self).save(*args, **kwargs)
        
    class Meta:
        verbose_name_plural = 'USERS WALLET SUMMARY'

