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
    class Meta:
        model = Poll
        fields = '__all__'


    def create(self, validated_data):
        # Ensure that the user who creates the poll is the request user
        validated_data['user'] = self.context['request'].user
        return super(PollSerializer, self).create(validated_data)


class SuggestedPollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poll
        fields = '__all__'