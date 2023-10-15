from rest_framework import serializers
from . models import *
from core.models import BlockedUser


# class BlockedUserOnlySerializer(serializers.ModelSerializer):
#     class Meta:
#         models = BlockedUser
#         fields = ['blocked_user']

from rest_framework import serializers
from .models import ChatSettings
from django.contrib.auth.models import User  # Assuming User is your user model

class ChatSettingsSerializer(serializers.ModelSerializer):
    blocked_users = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=BlockedUser.objects.all(),
        allow_null=True,
        required=False
    )
    
    # Add a field to include the usernames of blocked users
    blocked_user_usernames = serializers.SerializerMethodField()

    class Meta:
        model = ChatSettings
        fields = '__all__'
        read_only_fields = ('user',)  # Make the 'user' field read-only

    def get_blocked_user_usernames(self, obj):
        # Retrieve and return the usernames of blocked users
        return [blocked_user.blocked_user.username for blocked_user in obj.blocked_users.all()]
