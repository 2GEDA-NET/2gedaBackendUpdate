from django.shortcuts import render
from rest_framework import viewsets
from .models import BusinessDirectory, Address, PhoneNumber
from .serializers import *
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.authentication import *




class AddressViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

class PhoneNumberViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = PhoneNumber.objects.all()
    serializer_class = PhoneNumberSerializer

class BusinessDirectoryViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = BusinessDirectory.objects.all()
    serializer_class = BusinessDirectorySerializer
