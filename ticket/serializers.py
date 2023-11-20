from rest_framework import serializers
from .models import *
from typing import Any

class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = '__all__'


class AttendeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["category","price","quantity","is_sold"]


class EventSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    attendees = AttendeeSerializer(many=True, required=False)
    category = EventCategorySerializer(required=False)
    ticket = TicketSerializer(required=False)
    url = serializers.CharField(required=False)
    platform = serializers.CharField(required=False)
    desc = serializers.CharField(required=False)
    location = serializers.CharField(required=False)
    class Meta:
        model = Event
        fields = ["id","user","attendees","image","title","desc","platform","category","date","ticket","location","url"]
    
    def validate(self, attrs):
        error = {}
        if self.context["request"].method in ["POST"] and attrs.get("desc") is None:
            error['error'] = "desc field is required"
            raise serializers.ValidationError(error)
        if self.context["request"].method in ["POST"] and attrs.get("title") is None:
            error['error'] = "desc field is required"
            raise serializers.ValidationError(error)
        if self.context["request"].method in ["POST"] and attrs.get("platform") is None:
            error['error'] = "platform field is required"
            raise serializers.ValidationError(error)
        if self.context["request"].method in ["POST"] and attrs.get("location") is None:
            error['error'] = "location field is required"
            raise serializers.ValidationError(error)
        return super().validate(attrs)
    
    def create(self, validated_data):
        return super().create(validated_data)


class UserEventSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Event
        fields = ['images', 'title', 'desc', 'url', 'platform']


class EventListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [ 'title', 'desc', 'location', 'date', 'url']



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
        fields = ('id', 'user', 'amount', 'status', 'withdrawal_time')


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
