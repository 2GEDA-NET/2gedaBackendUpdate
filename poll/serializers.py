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
