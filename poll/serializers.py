from rest_framework import serializers
from .models import *
import requests
import json
from user.serializers import UserSerializer
from django.utils.timesince import timesince
from datetime import datetime 

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = '__all__'


class OptionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option_List
        fields = '__all__'


class VoteSerializer(serializers.ModelSerializer):
    cost = serializers.IntegerField(required=False)
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    class Meta:
        model = Voting
        fields = '__all__'


class PollMediaSerializer(serializers.ModelSerializer):

    class Meta:
        model = PollMedia
        fields = "__all__"


def validate_duration(duration:str, created_at):
    provided_datetime_str = str(created_at)
    provided_datetime = datetime.strptime(provided_datetime_str.replace("Z", "+0000"), "%Y-%m-%dT%H:%M:%S.%f%z")

    if duration.endswith("hours") and len(duration)==8:
        
        number = duration[:2]

        number =  int(number)
        new_datetime = provided_datetime + timedelta(hours=number)
        time_difference = new_datetime - provided_datetime

        if time_difference.total_seconds() > 86400:
            total_seconds = time_difference.days
            duration_time = timedelta(days=total_seconds)
            return f'{duration_time} days'
        
        elif time_difference.total_seconds() > 3600:
            total_seconds = time_difference.total_seconds()
            total_hours = total_seconds / 3600
            
            return f'{total_hours} hours'
        

        elif time_difference.total_seconds() < 3600:
            total_minute = time_difference.min
            
            return f'{total_hours} minutes'
    

    elif duration.endswith("hours") and len(duration)==7:
        number = duration[:1]

        number =  int(number)
        new_datetime = provided_datetime + timedelta(hours=number)
        time_difference = new_datetime - provided_datetime

        if time_difference.total_seconds() > 86400:
            total_seconds = time_difference.days
            duration_time = timedelta(days=total_seconds)
            return f'{duration_time} days'
        
        elif time_difference.total_seconds() > 3600:
            total_seconds = time_difference.total_seconds()
            total_hours = total_seconds / 3600
            
            return f'{total_hours} hours'
        

        elif time_difference.total_seconds() < 3600:
            total_minute = time_difference.min
            
            return f'{total_hours} minutes'
    
    
    elif duration.endswith("days") and len(duration)==6:
        number = duration[:1]
        number =  int(number)
        new_datetime = provided_datetime + timedelta(days=number)
        time_difference = new_datetime - provided_datetime

        if time_difference.total_seconds() > 86400:
            total_seconds = time_difference.days
            duration_time = timedelta(days=total_seconds)
            return f'{duration_time} days'
        
        elif time_difference.total_seconds() > 3600:
            total_seconds = time_difference.total_seconds()
            total_hours = total_seconds / 3600
            
            return f'{total_hours} hours'
        

        elif time_difference.total_seconds() < 3600:
            total_minute = time_difference.min
            
            return f'{total_hours} minutes'


    elif duration.endswith("days") and len(duration)==7:
        number = duration[:1]
        number =  int(number)
        new_datetime = provided_datetime + timedelta(days=number)
        time_difference = new_datetime - provided_datetime

        if time_difference.total_seconds() > 86400:
            total_seconds = time_difference.days
            duration_time = timedelta(days=total_seconds)
            return f'{duration_time} '
        
        elif time_difference.total_seconds() > 3600:
            total_seconds = time_difference.total_seconds()
            total_hours = total_seconds / 3600
            
            return f'{total_hours} hours'
        

        elif time_difference.total_seconds() < 3600:
            total_minute = time_difference.min
            
            return f'{total_minute} minutes'
    




class PollSerializer(serializers.ModelSerializer):
    # count_views = serializers.SerializerMethodField()
    
    media = PollMediaSerializer(required=False)
    options_list =  OptionListSerializer(required=False, many=True) 
    options =  OptionSerializer(required=False, many=True, read_only=True) 
    time_duration = serializers.DurationField(required=False)
    class Meta:
        model = Poll
        fields = "__all__"
    
    def get_count_views(self, obj):
        return obj.count_views()


    def create(self, validated_data):
        # Ensure that the user who creates the poll is the request user
        validated_data['user'] = self.context['request'].user
        return super(PollSerializer, self).create(validated_data)
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        username = representation.get("username")
        time_duration = representation.get("duration")
        time_created = representation.get("created_at")

        print("one")
        duration = validate_duration(time_duration, time_created)

        print("two")
        user_profile = UserProfile.objects.filter(user__username=username).first()
        #time
        time_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        print("three")
        time_instance = representation.get('time_stamp')
        print("Four")
        print(time_instance)
        time_object = datetime.strptime(time_instance, time_format)
        print(f'time_object is {time_object}')
        time_since = timesince(time_object)
        print(time_since)
        try:
            print(user_profile.media.profile_image)
            print(duration)
            data = {
                "profile_image": user_profile.media.profile_image,
                "time_since": time_since,
                "remaining_time": duration
            }
       
            representation.update(data)

        except:
            print(user_profile.media.profile_image,)
            data = {
                "time_since": time_since,
                "remaining_time": duration
            }
       
            representation.update(data)

        return representation


    
        


class SuggestedPollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poll
        fields = '__all__'


class AccessRequestSerializer(serializers.Serializer):
    poll_id = serializers.PrimaryKeyRelatedField(queryset=Poll.objects.all())
    
    def create(self, validated_data):
        user = self.context['request'].user
        poll = validated_data['poll']
        
        # Check if the user has already voted or requested access
        if user in poll.voters.all() or user in poll.access_requests.all():
            raise serializers.ValidationError("You have already voted or requested access to this poll.")
        
        return {'user': user, 'poll': poll}



class AccessApprovalSerializer(serializers.Serializer):
    poll_id = serializers.PrimaryKeyRelatedField(queryset=Poll.objects.all())
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    approval_status = serializers.BooleanField()

    def create(self, validated_data):
        user = self.context['request'].user
        poll = validated_data['poll']
        target_user = validated_data['user_id']
        approval_status = validated_data['approval_status']

        # Check if the user is the creator of the poll
        if user != poll.user:
            raise serializers.ValidationError("You do not have permission to approve/deny access requests.")
        
        # Check if the poll is private
        if poll.type != 'Private':
            raise serializers.ValidationError("Access requests can only be handled for private polls.")
        
        return {'poll': poll, 'user': target_user, 'approval_status': approval_status}


class PollCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poll
        fields = ('question', 'options', 'duration', 'type', 'media')

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class PollResultsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poll
        fields = ['id', 'question', 'options', 'type', 'created_at', 'is_active', 'is_ended', 'vote_count']


config = settings.PAYSTACK_SECRET_KEY

class PaystackPaymentSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default = serializers.CurrentUserDefault()
    )
    poll = PollSerializer(required=False)
    url = serializers.CharField(required=False)
    amount = serializers.IntegerField()
  
    class Meta:
        model = Instatiate_Payment
        fields = "__all__"

    
    def validate(self, attrs: dict):
        error = {}
        amount = attrs.get("amount")
        user = attrs.get("user")
        print(user.account_balance)

        headers = {
            'Authorization': f'Bearer {config}',
            'Content-Type': 'application/json',
        }

        ab = {"amount": amount, "email": user.email}
        data = json.dumps(ab)
        response = requests.post(
            'https://api.paystack.co/transaction/initialize', headers=headers, data=data)
        print(response.text)
        loaddata = json.loads(response.text)
        url = loaddata["data"]["authorization_url"] 

        if amount > user.account_balance:
            error["error"] = "Insufficient Balance"
            error["fund_account"] = url
            raise serializers.ValidationError(error)
    

    def create(self, validated_data):
 
        amount = validated_data["amount"]
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
        validated_data['is_instantiated'] = True


        return super().create(validated_data)

