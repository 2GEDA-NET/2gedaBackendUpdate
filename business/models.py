from django.db import models
from user.models import *

# Create your models here.

class BusinessOwnerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class BusinessDocument(models.Model):
    business = models.ForeignKey('BusinessDirectory', on_delete=models.CASCADE)
    document_type = models.CharField(max_length=100)
    document_file = models.FileField(upload_to='business_documents/')

    def __str__(self):
        return f"{self.document_type} - {self.business.name}"

class BusinessDirectory(models.Model):
    claimed_by = models.ForeignKey(BusinessOwnerProfile, blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    address = models.ForeignKey('Address', on_delete=models.CASCADE)
    phone_number = models.ForeignKey('PhoneNumber', on_delete=models.CASCADE)
    about = models.TextField()
    email = models.EmailField()
    website = models.URLField(blank=True, null=True)

    # Add other fields as needed

    def __str__(self):
        return self.name

class Address(models.Model):
    street = models.CharField(max_length=250)
    city = models.CharField(max_length=250)
    state = models.CharField(max_length=250)
    country = models.CharField(max_length=250)

    def __str__(self):
        # return str(self.street + ' ' + self.city + ' ' + self.state + ' '  + self.country)
        return self.id

class PhoneNumber(models.Model):
    phone_number1 = models.BigIntegerField(blank=True, null=True)
    phone_number2 = models.BigIntegerField(blank=True, null=True)
    phone_number3 = models.BigIntegerField(blank=True, null=True)
    phone_number4 = models.BigIntegerField(blank=True, null=True)


    def __str__(self):
        return self.phone_number1
