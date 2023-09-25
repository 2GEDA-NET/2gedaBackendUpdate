from rest_framework import serializers
from .models import *

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = '__all__'

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = '__all__'

class PollSerializer(serializers.ModelSerializer):
    count_views = serializers.SerializerMethodField()


    class Meta:
        model = Poll
        fields = '__all__'
    
    def get_count_views(self, obj):
        return obj.count_views()


    def create(self, validated_data):
        # Ensure that the user who creates the poll is the request user
        validated_data['user'] = self.context['request'].user
        return super(PollSerializer, self).create(validated_data)


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