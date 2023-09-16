from django.shortcuts import render

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Item, Vote
from .serializers import ItemSerializer, VoteSerializer

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

class VoteViewSet(viewsets.ModelViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer

    @action(detail=True, methods=['post'])
    def cast_vote(self, request, pk=None):
        item = self.get_object()
        user = request.user

        # Check if the user has already voted for this item
        if Vote.objects.filter(user=user, item=item).exists():
            return Response({'detail': 'You have already voted for this item.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new vote
        vote = Vote(user=user, item=item)
        vote.save()

        return Response({'detail': 'Vote recorded successfully.'}, status=status.HTTP_201_CREATED)
