# videolive/serializers.py
from rest_framework import serializers
from .models import *
from reward.models import Reward

class VideoSessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = VideoSession
        fields = '__all__'


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'  # You can specify fields explicitly if needed