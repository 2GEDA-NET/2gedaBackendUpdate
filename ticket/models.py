from collections.abc import Iterable
from django.db import models
from user.models import *
from django.utils import timezone
import secrets
from django.db import transaction
import uuid
from django.conf import settings


User = settings.AUTH_USER_MODEL


TICKET_CATEGORIES = (
    ('VIP', 'VIP'),
    ('STOCK', 'STOCK'),
    ('Regular', 'Regular'),
   
)

TICKET_TYPE = (
    ('FREE TICKET', 'FREE TICKET'),
    ('PAID TICKET', 'PAID TICKET'),
)

TICKET_STATUS = (
    ('SUCCESSFUL', 'SUCCESSFUL'),
    ('FAILED', 'FAILED'),
)


# Create your models here.
class EventCategory(models.Model):
    name = models.CharField(max_length=250)
    image = models.ImageField(upload_to='event-category-images/', blank=True, null=True)


class Get_Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    email = models.CharField(max_length=256, null=True, blank=True)
    quantity = models.IntegerField(default=0)
    address = models.CharField(max_length=256)
    ticket_type = models.CharField(default="FREE TICKET", choices=TICKET_TYPE, max_length=50)
    



class Ticket(models.Model):
    category = models.CharField(max_length=250, null=True, blank=True)
    price = models.IntegerField(default=0)
    quantity = models.IntegerField(default=0)
    is_sold = models.BooleanField(default=False, verbose_name='Ticket Sold')
    ticket_sales = models.ManyToManyField(Get_Ticket)
    ticket_key = models.UUIDField(default=uuid.uuid4())
    is_free = models.BooleanField(default=False)

    def save(self, *args, **kwargs) -> None:

        if self.is_free == True:
            self.price = 0
        return super().save(*args, **kwargs)
    

def formatted_datetime():
    return self.your_datetime_field.strftime('%d %b, %Y')


class Ticket_Issues(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=256)
    error_key = models.UUIDField(default=uuid.uuid4())



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
    ticket = models.ForeignKey('Ticket', on_delete=models.CASCADE , related_name="old_ticket", null=True)
    each_ticket = models.ManyToManyField(Ticket)
    event_key = models.CharField(max_length=256, null=True)
    is_public = models.BooleanField(default=False)
    add_to_sales = models.BooleanField(default=True)
    sales = models.ManyToManyField("Ticket_Payment")
    formated_date  =  models.CharField(default=str(timezone.now().strftime('%d %b, %Y')))
    


    def save(self, *args, **kwargs):
        if not self.pk:
            generated_uuid = str(uuid.uuid4())

            random_string = generated_uuid[:10].upper()

            self.event_key = random_string

        super().save(*args, **kwargs)



class Bank(models.Model):
    name = models.CharField(max_length=250)
    bank_code = models.BigIntegerField(unique=True)

ACCOUNT_TYPE = (
    ('Savings', 'Savings'),
    ('Current', 'Current'),
)


class PayOutInfo(models.Model):
    user =  models.ForeignKey(User, on_delete=models.CASCADE)
    bank_name = models.CharField(max_length=256, null=True, blank=True)
    account_name = models.CharField(max_length=256, null=True, blank=True)
    account_number = models.CharField(max_length=256, null=True, blank=True)
    account_type = models.CharField(max_length=256, null=True, blank=True)


class UserWallet(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    currency = models.CharField(max_length=50, default='NGN')
    balance =  models.FloatField(default=0)
    prev_balance = models.FloatField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    last_fund = models.DateTimeField(null=True, blank=True)
    

    def __str__(self):
        return self.user.__str__()

    @classmethod
    def withdraw(cls, id, amount):
        with transaction.atomic():
            account = (cls.objects.select_for_update().get(id=id))
            print(account)
            balance_before = account.balance
            if account.balance < amount or amount < 0:
                return False
            account.balance -= amount
            account.save()

    @classmethod
    def deposit(cls, id, amount):
        with transaction.atomic():
            account = (cls.objects.select_for_update().get(id=id))
            print(account)
            account.prev_balance = account.balance
            if amount < 0:
                return False
            account.balance += amount
            account.user.account_balance = account.balance
            account.save()


class Event_Transaction_History(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    currency = models.CharField(max_length=50, default='NGN')
    balance =  models.FloatField(default=0)
    prev_balance = models.FloatField(default=0)
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, null=True)
    transaction_status = models.CharField(choices=TICKET_STATUS, default="FAILED")
    transaction_id = models.CharField(max_length=256, null=True)



class Ticket_Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    amount = models.FloatField()
    total_amount = models.FloatField(default=0)
    time_stamp = models.DateTimeField(default=timezone.now)
    url = models.CharField(max_length=1000, null=True, blank=True)
    is_initiated = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    payment_id = models.UUIDField(default=uuid.uuid4())
    ticket_quantity = models.IntegerField(default=0)

    class Meta:
        get_latest_by = 'time_stamp'

    def save(self, *args, **kwargs) -> None:
        if self.ticket_quantity and self.amount:
            self.amount = self.ticket_quantity * self.amount
            
        return super().save(*args, **kwargs)


class Withdraw(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    details = models.ForeignKey(PayOutInfo, on_delete=models.CASCADE)
    amount = models.BigIntegerField()
    is_successful = models.BooleanField(default=False, verbose_name='SUCCESSFUL')
    is_pending = models.BooleanField(default=False, verbose_name='PENDING')
    is_failed = models.BooleanField(default=False, verbose_name='FAILED')
    time_stamp = models.DateTimeField(default=timezone.now)
    class Meta:
        get_latest_by = 'time_stamp'

    # def save(self, *args, **kwargs) -> None:

    #     if Withdraw.objects.filter(user=self.user) is not None:
    #         user = Withdraw.objects.filter(user=self.user).latest() 
    #         if user.is_pending == False:
    #             pass
    #         else:
    #             return super().save(*args, **kwargs)

    #     else:
    #         return super().save(*args, **kwargs)


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
 

class Ticket_Sales_Ticket(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    desc = models.CharField(max_length=256, null=True)
    platform = models.CharField(max_length=256, null=True)
    category = models.CharField(max_length=256, null=True)
    location = models.CharField(max_length=256, null=True)
    url = models.CharField(max_length=256, null=True)
    ticket = models.CharField(max_length=256, null=True)
    event_key = models.CharField(max_length=256, null=True)
    ticket_key = models.CharField(max_length=256, null=True)
    ticket_category = models.CharField(max_length=256, null=True)
    ticket_price = models.CharField(max_length=256, null=True)
    ticket_quantity = models.CharField(max_length=256, null=True)
    ticket_ticket_key = models.CharField(max_length=256, null=True)
    event_key = models.CharField(max_length=256, null=True)

    def save(self, *args, **kwargs) -> None:
        if self.event_key:
            event = Event.objects.get(event_key=self.event_key)
            event.attendees.add(self.user)
            event.save()
            user_wallet = None
            if not UserWallet.objects.get(user=event.user).DoesNotExist():
                user_wallet = UserWallet.objects.get(user=event.user)
            else:
                user_wallet = UserWallet.objects.create(user=event.user)
            user_wallet.deposit(amount=event.ticket.price)
        return super().save(*args, **kwargs)
    