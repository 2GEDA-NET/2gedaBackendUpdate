from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.utils import timezone
from location_field.models.plain import PlainLocationField
from django.utils.translation import gettext as _
from django.conf import settings



class UserModel(AbstractUser):
    username = models.CharField(unique=True, max_length=15)
    phone = models.CharField(max_length=15, blank=True, null=False)
    email = models.EmailField(blank=True, null=False)
    password = models.CharField(max_length=250, validators=[MinLengthValidator(7, message='Your password is too short! Minimum of 7 length is required')])
    is_verified = models.BooleanField(default=False, verbose_name='Verified')
    is_admin = models.BooleanField(default=False, verbose_name='Admin Account')
    is_verified = models.BooleanField(default=False, verbose_name='Verified')
    last_seen = models.DateTimeField(null=True, blank=True)
    is_business = models.BooleanField(
        default=False, verbose_name='Business Account')
    is_personal = models.BooleanField(
        default=False, verbose_name='Personal Account')
    
    # resend_count = models.PositiveIntegerField(default=0)
    # registration_timestamp = models.DateTimeField(auto_now_add=True)
    
    REQUIRED_FIELDS = ['email', 'phone']

    def __str__(self):
        return f'{self.email} {self.phone} {self.username}'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['email', 'phone'],
                name='unique_email_or_phone',
                condition=models.Q(email__isnull=False) | models.Q(phone__isnull=False)
            )
        ]


class OtpReceiver(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    otp = models.CharField(max_length=90, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Password reset for {self.user.username}"


class ProfileMedia(models.Model):
    media = models.FileField(upload_to='profile_files/', blank=True, null=True)


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

class UserProfile(models.Model):
    # Create a one-to-one relationship with the User model
    user = models.OneToOneField(UserModel, on_delete=models.CASCADE)
    work = models.CharField(max_length=255, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=15, choices=GENDER_CHOICES, blank=True, null=True)
    custom_gender = models.CharField(max_length=250, blank=True, null=True)
    religion = models.CharField(
        max_length=20, choices=RELIGION_CHOICES, verbose_name='Religion')
    media = models.ForeignKey(ProfileMedia, on_delete= models.CASCADE, blank=True, null=True)
    address = models.ForeignKey('Address', on_delete = models.CASCADE, null = True)
    stickers = models.ManyToManyField('self', related_name='sticking', symmetrical=False)
    is_flagged = models.BooleanField(default=False, verbose_name='Flagged')
    favorite_categories = models.ManyToManyField('BusinessCategory', related_name='users_with_favorite', blank=True)
    searched_polls = models.ManyToManyField('poll.Poll', related_name='users_searched', blank=True)

    class Meta:
        def __str__(self):
            return self.user.username


    def sticker_count(self):
        return self.stickers.count()

    def sticking_count(self):
        return UserProfile.objects.filter(stickers=self.user).count()
    
    


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

    # def __str__(self):
    #     return f"Availability for {self.user.username}"



class BusinessAccount(models.Model):
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    role = models.CharField(max_length=250)
    image = models.ImageField(
        upload_to='business_profile/', blank=True, null=True)
    business_category = models.ForeignKey(
        BusinessCategory, on_delete=models.CASCADE)
    business_availability = models.OneToOneField(BusinessAvailability, on_delete=models.CASCADE)
    year_founded = models.DateField(blank=True, null=True)
    business_name = models.CharField(max_length=250)
    business_password = models.CharField(max_length=200)
    business_address = models.ForeignKey('Address', on_delete = models.CASCADE, related_name= 'Address', verbose_name='Business Address')


class Address(models.Model):
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
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
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
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    category = models.CharField(max_length=250, choices=DEVICE_CATEGORY)
    inputs = models.CharField(max_length=250)


class Notification(models.Model):
    recipient = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='notifications_received')
    sender = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='notifications_sent')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification to {self.recipient.username} from {self.sender.username}: {self.message}"


class BlockedUser(models.Model):
    blocker = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='blocked_users')
    blocked_user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='blockers')
    reason = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.blocker} blocked {self.blocked_user}"

    class Meta:
        unique_together = ('blocker', 'blocked_user')