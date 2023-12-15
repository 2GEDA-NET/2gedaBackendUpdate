from collections.abc import Iterable
import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.utils.translation import gettext as _
from django.conf import settings
from .managers import UserManager
from location_field.models.plain import PlainLocationField
from storages.backends.s3boto3 import S3Boto3Storage
from ticket.models import UserWallet
from django.db import transaction
import secrets
import string
from django.utils import timezone

def generate_random_string(length=7):
    characters = string.ascii_letters + string.digits + string.punctuation
    random_string = ''.join(secrets.choice(characters) for _ in range(length))
    return random_string

class BusinessCategory(models.Model):
    name = models.CharField(max_length=250)
    desc = models.TextField()

    def __str__(self):
        return self.name


GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Rather not say', 'Rather not say'),
)


DAYS_OF_THE_WEEK_CHOICES = (
    ('Sunday', 'Sunday'),
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
    ('Saturday', 'Saturday'),
)


class BusinessCategory(models.Model):
    name = models.CharField(max_length=250)
    desc = models.TextField()

    def __str__(self):
        return self.name

RELIGION_CHOICES = [
    ('Christianity', 'Christianity'),
    ('Muslim', 'Muslim'),
    ('Indigenous', 'Indigenous'),
    ('Others', 'Others'),
]

Currency = (
    ("NGN","NGN"),
    ("USD", "USD")
)

Fund_Type = (
    ("debit", "debit"),
    ("credit", "credit")
)

# Create your models here.
class UserWallet(models.Model):
    user = models.ForeignKey("User", null=True, on_delete=models.CASCADE, related_name="user_wallet")
    currency = models.CharField(max_length=50, choices=Currency, default='NGN')
    balance =  models.FloatField(default=0)
    prev_balance = models.FloatField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    last_fund = models.DateTimeField(null=True, blank=True)
    type = models.CharField(max_length=50, choices=Fund_Type, default='NGN')



class ProfileMedia(models.Model):
    media = models.FileField(upload_to='profile_files/', blank=True, null=True)


class User(AbstractUser):
    email = models.EmailField(unique=True, null=True, blank=True)
    is_business = models.BooleanField(
        default=False, verbose_name='Business Account')
    is_personal = models.BooleanField(
        default=False, verbose_name='Personal Account')
    is_admin = models.BooleanField(default=False, verbose_name='Admin Account')
    phone_number = models.BigIntegerField(unique=True, null=True, blank=True)
    is_verified = models.BooleanField(default=False, verbose_name='Verified')
    last_seen = models.DateTimeField(null=True, blank=True)
    otp = models.CharField(max_length=5, blank=True)
    otp_verified = models.BooleanField(default=False)
    secret_key = models.CharField(default=generate_random_string)
    account_balance = models.IntegerField(default=0)
    previous_balance = models.IntegerField(default=0)
    work = models.CharField(max_length=255, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True,)
    gender = models.CharField(
        max_length=15, choices=GENDER_CHOICES, blank=True, null=True)
    custom_gender = models.CharField(max_length=250, blank=True, null=True)
    religion = models.CharField(
        max_length=20, null=True, choices=RELIGION_CHOICES, verbose_name='Religion')
    media = models.ManyToManyField("UserProfileImage", related_name='user_profile_media')
    cover_image = models.ForeignKey("UserCoverImage", on_delete=models.CASCADE, blank=True, null=True, related_name='users_image')
    address = models.ForeignKey('Address', on_delete=models.CASCADE, null=True, related_name='home_address')
    stickers = models.ManyToManyField('self', related_name='sticking',null=True,  symmetrical=False)
    is_flagged = models.BooleanField(default=False, verbose_name='Flagged_User')
    favorite_categories = models.ManyToManyField(BusinessCategory, related_name='users_favorite', blank=True, null=True)
    searched_polls = models.ManyToManyField('poll.Poll', related_name='user_searched', blank=True)
    has_updated_profile = models.BooleanField(default=False)
    bio = models.TextField(null=True)

    class Meta:
        swappable = 'AUTH_USER_MODEL'
    

    @classmethod
    def withdraw(cls, id, amount):
        with transaction.atomic():
            account = (cls.objects.select_for_update().get(id=id))
            print(account)
            account.previous_balance = account.account_balance
            if account.account_balance < amount or amount < 0:
                return False
            account.account_balance -= amount
            account.save()
            UserWallet.objects.create(user=account,type="credit", prev_balance=account.previous_balance, balance=account.account_balance)


    @classmethod
    def fund(cls, id, amount):
        with transaction.atomic():
            account = (cls.objects.select_for_update().get(id=id))
            print(account)
            account.previous_balance = account.account_balance
            if amount < 0:
                return False
            
            account.account_balance += amount
            account.save()
            UserWallet.objects.create(user=account,type="credit", prev_balance=account.previous_balance, balance=account.account_balance)



GENDER_CHOICES = (
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Rather not say', 'Rather not say'),
)


DAYS_OF_THE_WEEK_CHOICES = (
    ('Sunday', 'Sunday'),
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
    ('Saturday', 'Saturday'),
)




RELIGION_CHOICES = [
    ('Christianity', 'Christianity'),
    ('Muslim', 'Muslim'),
    ('Indigenous', 'Indigenous'),
    ('Others', 'Others'),
]

class UserCoverImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cover_image = models.ImageField(upload_to='cover_image/', storage=S3Boto3Storage() )


class UserProfileImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='cover_image/', storage=S3Boto3Storage() )


class UserProfile(models.Model):
    # Create a one-to-one relationship with the User model
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    work = models.CharField(max_length=255, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True,)
    gender = models.CharField(
        max_length=15, choices=GENDER_CHOICES, blank=True, null=True)
    custom_gender = models.CharField(max_length=250, blank=True, null=True)
    religion = models.CharField(
        max_length=20, choices=RELIGION_CHOICES, verbose_name='Religion')
    media = models.ForeignKey(UserProfileImage, on_delete=models.CASCADE, blank=True, null=True, related_name='user_media')
    cover_image = models.ForeignKey(UserCoverImage, on_delete=models.CASCADE, blank=True, null=True, related_name='user_cover_image')
    address = models.ForeignKey('Address', on_delete=models.CASCADE, null=True, related_name='user_address')
    stickers = models.ManyToManyField('self', related_name='sticking', symmetrical=False)
    is_flagged = models.BooleanField(default=False, verbose_name='Flagged')
    favorite_categories = models.ManyToManyField('BusinessCategory', related_name='users_with_favorite', blank=True)
    searched_polls = models.ManyToManyField('poll.Poll', related_name='users_searched', blank=True)
    has_updated_profile = models.BooleanField(default=False)

    def save(self, *args, **kwargs) -> None:
        UserWallet.objects.create(user=self.user)

        return super().save(*args, **kwargs)



    def sticker_count(self):
        return self.stickers.count()

    def sticking_count(self):
        return UserProfile.objects.filter(stickers=self.user).count()
    
    def profile_image(self):
        return self.media.profile_image
    
    # @property
    # def date_of_birth(self):
    #     return self._date_of_birth.strftime('%Y-%m-%d')

    # @date_of_birth.setter
    # def date_of_birth(self, value):
    #     self._date_of_birth = datetime.datetime.strptime(value, '%Y-%m-%d').date()
        
    def __str__(self):
        return self.user.username


class BusinessAvailability(models.Model):
    always_available = models.BooleanField(default=False)
    # Define availability for each day of the week
    # sunday
    sunday = models.BooleanField(default=False)
    sunday_open = models.TimeField(null=True, blank=True)
    sunday_close = models.TimeField(null=True, blank=True)
    # monday
    monday = models.BooleanField(default=False)
    monday_open = models.TimeField(null=True, blank=True)
    monday_close = models.TimeField(null=True, blank=True)
    # tuesday
    tuesday = models.BooleanField(default=False)
    tuesday_open = models.TimeField(null=True, blank=True)
    tuesday_close = models.TimeField(null=True, blank=True)
    # wednesday
    wednesday = models.BooleanField(default=False)
    wednesday_open = models.TimeField(null=True, blank=True)
    wednesday_close = models.TimeField(null=True, blank=True)
    # thursday
    thursday = models.BooleanField(default=False)
    thursday_open = models.TimeField(null=True, blank=True)
    thursday_close = models.TimeField(null=True, blank=True)
    # friday
    friday = models.BooleanField(default=False)
    friday_open = models.TimeField(null=True, blank=True)
    friday_close = models.TimeField(null=True, blank=True)
    # saturday
    saturday = models.BooleanField(default=False)
    saturday_open = models.TimeField(null=True, blank=True)
    saturday_close = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"Availability for {self.user.username}"



class BusinessAccount(models.Model):
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    role = models.CharField(max_length=250)
    image = models.ImageField(
        upload_to='business_profile/', blank=True, null=True)
    business_category = models.ForeignKey(
        BusinessCategory, on_delete=models.CASCADE)
    business_availability = models.OneToOneField('BusinessAvailability', on_delete=models.CASCADE)
    year_founded = models.DateField(blank=True, null=True)
    business_name = models.CharField(max_length=250)
    business_password = models.CharField(max_length=200)
    # business_address = models.ForeignKey('Address', on_delete = models.CASCADE, related_name= 'Address', verbose_name='Business Address')


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='address_user')
    country = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    current_city = models.CharField(max_length=100, null=True, blank=True)
    street_address = models.CharField(max_length=100, null=True, blank=True)
    apartment_address = models.CharField(max_length=100, null=True, blank=True)
    location = PlainLocationField(based_fields=['current_city'], zoom=7, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ('-created_at', )
    
    def __str__(self):
        components = []
        if self.country:
            components.append(self.country)
        if self.city:
            components.append(self.city)
        if self.street_address:
            components.append(self.street_address)
        if self.apartment_address:
            components.append(self.apartment_address)
        if self.postal_code:
            components.append(self.postal_code)
        return ', '.join(components)



class ReportedUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()
    is_banned = models.BooleanField(default=False, verbose_name='Banned')
    is_disabled = models.BooleanField(default=False, verbose_name='Disabled')

class Verification(models.Model):
    profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    legal_name = models.CharField(max_length=250)
    work = models.CharField(max_length=250)
    link1 = models.URLField(max_length=250)
    link2 = models.URLField(max_length=250)
    link3 = models.URLField(max_length=250)
    media = models.ImageField(upload_to='verificationImage/', blank=True, null=True)

DEVICE_CATEGORY = (
    ('IMEI', 'IMEI'),
    ('SERIAL NUMBER', 'SERIAL NUMBER')
)

class Device(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    category = models.CharField(max_length=250, choices=DEVICE_CATEGORY)
    input = models.CharField(max_length=250)


class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications_received')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications_sent', null=True, blank=True)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification to {self.recipient.username} from {self.sender.username}: {self.message}"


class BlockedUser(models.Model):
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_users')
    blocked_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blockers')
    reason = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.blocker} blocked {self.blocked_user}"

    class Meta:
        unique_together = ('blocker', 'blocked_user')


class UserGeoInformation(models.Model):
    city =  models.CharField(max_length=250, null=True)
    city_ascii =  models.CharField(max_length=250, null=True)
    lat = models.CharField(max_length=250, null=True)
    lng = models.CharField(max_length=250, null=True)
    country = models.CharField(max_length=250, null=True)
    iso2 = models.CharField(max_length=250, null=True)
    iso3 = models.CharField(max_length=250, null=True)
    admin_name = models.CharField(max_length=250, null=True)
    capital = models.CharField(max_length=250, null=True)
    population = models.CharField(max_length=250, null=True)
    mid = models.CharField(max_length=250, null=True)