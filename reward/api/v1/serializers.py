from rest_framework import serializers
from reward.models import Reward, Claim_Reward_Model
from typing import Any
from user.models import User
from django.db.models import Count

medium_list = [
        "login",
        "post_creation",
        "comments",
        "stick",
        "likes",
        "stickers",
        "time_rewards",
        "commerce",
        "start_livestream",
        "end_livestream",
        "buy_tickets",
        "sell_tickets",
        "stereo"
    ]

#mediums and their minimum claim value
medium_dict = {
        "login": 1,
        "post_creation": 1,
        "comments": 20,
        "stick": 25,
        "likes": 50,
        "stickers": 25,
        "time_rewards": 2,
        "commerce": 1,
        "start_livestream": 1,
        "engage_livestream": 1,
        "buy_tickets": 1,
        "sell_tickets": 1,
        "stereo": 1
}

class Reward_Serializers(serializers.ModelSerializer):

    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Reward
        fields = ('medium','user')

    # def get_user(self, obj):
    #     # Access the user from the request object
    #     request = self.context.get('request')
    #     if request and request.user.is_authenticated:
    #         print("Trrrgwdhlq")
    #         return request.user.username
    #     return None

    def validate(self, attrs: dict[str, Any]):
        errors = {}


        if not attrs.get("medium"):
            errors["error"] = f"requires atleast one of these field -> {medium_list}"
            raise serializers.ValidationError(errors)

        return super().validate(attrs)
    


class Claim_Reward_Serializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default = serializers.CurrentUserDefault()
    )
    class Meta:
        model = Claim_Reward_Model
        fields = ("claims", "medium", "user")

    def create(self, validated_data):
        instance = Claim_Reward_Model(**validated_data)
        if instance.medium in medium_list:
            instance.claims = medium_dict[instance.medium]
            instance.save()
            return  instance
        

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        error = {}
        medium = attrs.get("medium")
        claims = attrs.get("claims")
        user = attrs.get("user")
        if medium not in medium_list:
            error["errors"] = "Invalid Claim type"
            raise serializers.ValidationError(error)

        if Reward.objects.filter(user=user, medium=medium).count() < medium_dict[medium]:
            error["errors"] = "you need more points to claim this reward"
            raise serializers.ValidationError(error)


        if claims < medium_dict[str(medium)]:
            error["errors"] = "you need more points to claim this reward"
            raise serializers.ValidationError(error)
        
        
        return super().validate(attrs)
    
    def to_representation(self, instance):
        data = {**super().to_representation(instance)}
        data.update({
            "claimed": "true"
        })
        return data