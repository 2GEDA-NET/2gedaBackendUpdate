from rest_framework import serializers
from .models import *

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = '__all__'


class LifeStyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = LifeStyle
        fields = '__all__'


class ThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread
        fields = '__all__'


class BroadcastPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = BroadcastPlan
        fields = '__all__'