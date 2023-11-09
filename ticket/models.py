from django.db import models
from user.models import *

# Create your models here.
class EventCategory(models.Model):
    name = models.CharField(max_length=250)
    image = models.ImageField(upload_to='event-category-images/', blank=True, null=True)


class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    attendees = models.ManyToManyField(User, related_name='attended_events', blank=True)
    image = models.ImageField(upload_to='event-images/', blank=True, null=True)
    title = models.CharField(max_length=250)
    desc = models.TextField()
    platform = models.CharField(max_length=300)
    category = models.ForeignKey(EventCategory, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)
    location = models.CharField(max_length=250, blank=True, null=True)
    url = models.URLField(max_length=250, blank=True, null=True)
    is_popular = models.BooleanField(default=False, verbose_name='Popular')
    is_promoted = models.BooleanField(default=False, verbose_name='Promoted')
    ticket = models.ForeignKey('Ticket', on_delete=models.CASCADE)


TICKET_CATEGORIES = (
    ('VIP', 'VIP'),
    ('Stock', 'Stock'),
)

TICKET_TYPE = (
    ('FREE TICKET', 'FREE TICKET'),
    ('PAID TICKET', 'PAID TICKET'),
)

class Ticket(models.Model):
    category = models.CharField(max_length=250, choices=TICKET_CATEGORIES)
    price = models.IntegerField()
    quantity = models.IntegerField()
    is_sold = models.BooleanField(default=False, verbose_name='Ticket Sold')

class Bank(models.Model):
    name = models.CharField(max_length=250)
    bank_code = models.BigIntegerField(unique=True)

ACCOUNT_TYPE = (
    ('Savings', 'Savings'),
    ('Current', 'Current'),
)

class PayOutInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bank_name = models.ForeignKey(Bank, on_delete=models.CASCADE)
    account_name = models.CharField(max_length=250, blank=True, null=True)
    account_number = models.BigIntegerField()
    account_type = models.CharField(max_length= 250, choices=ACCOUNT_TYPE)

class Withdraw(models.Model):
    details = models.ForeignKey(PayOutInfo, on_delete=models.CASCADE)
    amount = models.BigIntegerField()
    is_successful = models.BooleanField(default=False, verbose_name='SUCCESSFUL')
    is_pending = models.BooleanField(default=False, verbose_name='PENDING')
    is_failed = models.BooleanField(default=False, verbose_name='FAILED')


class WithdrawalHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='Pending', choices=[
        ('Pending', 'Pending'),
        ('Successful', 'Successful'),
        ('Failed', 'Failed'),
    ])
    withdrawal_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Withdrawal by {self.user.username} at {self.withdrawal_time}"


class WithdrawalRequest(models.Model):
    details = models.ForeignKey(PayOutInfo, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='Pending', choices=[
        ('Pending', 'Pending'),
        ('Successful', 'Successful'),
        ('Failed', 'Failed'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Withdrawal Request by {self.user.username}"



class TicketPurchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)  # Assuming you have an Event model
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE) 
    payment_status = models.CharField(max_length=250, default='Pending', choices=[('Pending', 'Pending'), ('Successful', 'Successful'), ('Failed', 'Failed')])
    payment_details = models.TextField(blank=True, null=True)
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket Purchase by {self.user.username} for {self.ticket.title} on {self.purchase_date}"

    class Meta:
        verbose_name_plural = "Ticket Purchases"

class EventPromotionRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    request_date = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Promotion Request for '{self.event.title}' by {self.user.username}"