from django.db import models

# Create your models here.
class BusinessDirectory(models.Model):
    name = models.CharField(max_length=250)
    address = models.ForeignKey('Address', on_delete=models.CASCADE)
    phone_number = models.ForeignKey('PhoneNumber', on_delete=models.CASCADE)
    about = models.TextField()

class Address(models.Model):
    street = models.CharField(max_length=250)
    city = models.CharField(max_length=250)
    state = models.CharField(max_length=250)
    country = models.CharField(max_length=250)

    def __str__(self):
        return str(self.street + ' ' + self.city + ' ' + self.state + ' '  + self.country)

class PhoneNumber(models.Model):
    phone_number1 = models.BigIntegerField(blank=True, null=True)
    phone_number2 = models.BigIntegerField(blank=True, null=True)
    phone_number3 = models.BigIntegerField(blank=True, null=True)
    phone_number4 = models.BigIntegerField(blank=True, null=True)