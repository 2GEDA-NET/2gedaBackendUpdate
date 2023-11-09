from django.shortcuts import render
from rest_framework import generics 
from rest_framework.permissions import (
    IsAuthenticated,
)
from .serializers import (
    Reward_Serializers,
    Claim_Reward_Serializer
)
from reward.models import (
    Reward,
    Claim_Reward_Model
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count
# Create your views here.

class Reward_User(generics.CreateAPIView):
    queryset = Reward.objects.all()
    serializer_class = Reward_Serializers
    permission_classes = (IsAuthenticated,)

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)
    

class Get_Rewards(APIView):
    permission_classes = [IsAuthenticated,]
    def get(self, request:Request, format=None) -> Response: 
        error = {}
        try:
            if request.GET.get("medium") is not None:
                medium =  request.GET.get("medium")
                rewards = Reward.objects.filter(medium=medium, user=request.user).order_by('-time_stamp').values()
                return Response(list(rewards), status=200)

            all_rewards = Reward.objects.filter(user=request.user).values()
            return Response(list(all_rewards), status=200)
        except Exception as e:
            print(e)
            error["error"] = "Cant fetch data"
            return Response(error, status=500)
        

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
        "engage_livestream",
        "buy_tickets", 
        "sell_tickets",
        "stereo", 
  ]      


class Get_All_Rewards(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request:Request, format=None) -> Response:
        counts = Reward.objects.filter(medium__in=medium_list).values("medium").annotate(counts=Count("medium"))

        return Response(list(counts), status=200)


class Get_All_Rewards(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request:Request, format=None) -> Response:
        counts = Reward.objects.filter(medium__in=medium_list).values("medium").annotate(counts=Count("medium"))

        return Response(list(counts), status=200)


class Get_Each_Rewards(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request:Request, format=None) -> Response:
        counts = Reward.objects.filter(medium__in=medium_list).values("medium").annotate(counts=Count("medium"))

        return Response(list(counts), status=200)


class Claim_Reward(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = Claim_Reward_Serializer
    queryset = Claim_Reward_Model.objects.all()


class Claims_Record(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        claim = Claim_Reward_Model.objects.filter(user=request.user)
        
        history = claim.values()

        return Response(list(history), status=200)






