from rest_framework import serializers
from .models import *

class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
    
class UserEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['images', 'title', 'desc', 'url', 'platform']


class EventListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [ 'title', 'desc', 'location', 'date', 'url']


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'

class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = '__all__'

class PayOutInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayOutInfo
        fields = '__all__'

class WithdrawSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdraw
        fields = '__all__'


class WithdrawalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawalHistory
        fields = ('id', 'user', 'amount', 'withdrawal_time')


class WithdrawalRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawalRequest
        fields = ['ticket_purchase', 'user', 'amount', 'status', 'created_at']
        read_only_fields = ['user', 'status', 'created_at']


class EventPromotionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventPromotionRequest
        fields = '__all__' 

class TicketPurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketPurchase
        fields = ['user', 'ticket']

    def create(self, validated_data):
        # Override the create method to handle the creation of the TicketPurchase instance
        ticket_purchase = TicketPurchase.objects.create(**validated_data)
        return ticket_purchase
