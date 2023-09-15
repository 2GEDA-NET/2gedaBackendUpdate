from django.shortcuts import render
from rest_framework import viewsets
from .models import EventCategory, Event, Ticket, Bank, PayOutInfo, Withdraw
from .serializers import EventCategorySerializer, EventSerializer, TicketSerializer, BankSerializer, PayOutInfoSerializer, WithdrawSerializer

class EventCategoryViewSet(viewsets.ModelViewSet):
    queryset = EventCategory.objects.all()
    serializer_class = EventCategorySerializer

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

class BankViewSet(viewsets.ModelViewSet):
    queryset = Bank.objects.all()
    serializer_class = BankSerializer

class PayOutInfoViewSet(viewsets.ModelViewSet):
    queryset = PayOutInfo.objects.all()
    serializer_class = PayOutInfoSerializer

class WithdrawViewSet(viewsets.ModelViewSet):
    queryset = Withdraw.objects.all()
    serializer_class = WithdrawSerializer
