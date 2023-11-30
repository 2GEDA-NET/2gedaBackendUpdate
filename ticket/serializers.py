from rest_framework import serializers
from .models import *
from typing import Any
import json
import requests
from django.conf import settings

config = settings.PAYSTACK_SECRET_KEY

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
        fields = ["id","category","price","quantity","is_sold"]


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
    each_ticket = TicketSerializer(required=False, many=True)

    class Meta:
        model = Event
        fields = "__all__"
    
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
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        event_key = instance.event_key
        price = instance.ticket.price
        share = {
            "url" : f'https://www.2geda.net/ticket/get-ticket?event={event_key}&amount={price}'
        } 
        representation["share"] = share
        return representation
    



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


class PaystackPaymentSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default = serializers.CurrentUserDefault()
    )
    ticket = TicketSerializer(required=False)
    url = serializers.CharField(required=False) 
    is_initiated = serializers.BooleanField(required=False) 

    class Meta:
        model = Ticket_Payment
        fields = "__all__"

    def validate(self, attrs):
        user = attrs.get("user")
        ticket = attrs.get("ticket")
        error = {}

        return super().validate(attrs)
    
    def create(self, validated_data):
      
        ticket = validated_data['ticket']
        amount = ticket.price
        user = validated_data["user"]
        email = user.email

        headers = {
            'Authorization': f'Bearer {config}',
            'Content-Type': 'application/json',
        }

        ab = {"amount": amount, "email": email}
        data = json.dumps(ab)
        response = requests.post(
            'https://api.paystack.co/transaction/initialize', headers=headers, data=data)
        print(response.text)
        loaddata = json.loads(response.text)
        url = loaddata["data"]["authorization_url"]
        validated_data['url'] = url
        validated_data['is_initiated'] = True
        return super().create(validated_data)



class WithdrawSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default = serializers.CurrentUserDefault()
    )
    details = PayOutInfoSerializer(required=False)    

    class Meta:
        model = Withdraw
        fields = "__all__"

    