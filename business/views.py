from django.shortcuts import render
from rest_framework import viewsets
from .models import BusinessDirectory, Address, PhoneNumber
from .serializers import *



class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

class PhoneNumberViewSet(viewsets.ModelViewSet):
    queryset = PhoneNumber.objects.all()
    serializer_class = PhoneNumberSerializer

class BusinessDirectoryViewSet(viewsets.ModelViewSet):
    queryset = BusinessDirectory.objects.all()
    serializer_class = BusinessDirectorySerializer
