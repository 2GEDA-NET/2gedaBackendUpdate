from django.shortcuts import render
from rest_framework.generics import *
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework import viewsets
from rest_framework.authentication import *
from .models import EventCategory, Event, Ticket, Bank, PayOutInfo, Withdraw
from .serializers import EventCategorySerializer, EventSerializer, TicketSerializer, BankSerializer, PayOutInfoSerializer, WithdrawSerializer

class EventCategoryViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = EventCategory.objects.all()
    serializer_class = EventCategorySerializer

class EventViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class TicketViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

class BankViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Bank.objects.all()
    serializer_class = BankSerializer

class PayOutInfoViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = PayOutInfo.objects.all()
    serializer_class = PayOutInfoSerializer

class WithdrawViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Withdraw.objects.all()
    serializer_class = WithdrawSerializer
