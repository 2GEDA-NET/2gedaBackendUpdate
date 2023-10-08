from django.test import TestCase

# Create your tests here.

class Authencity(models.Model):
    email = models.EmailField(unique=True)
    password = models
