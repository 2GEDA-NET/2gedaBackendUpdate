from rest_framework import generics
from .models import Option, Vote, Poll
from .serializers import *

class OptionListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Option.objects.all()
    serializer_class = OptionSerializer

class OptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Option.objects.all()
    serializer_class = OptionSerializer

class VoteListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer

class VoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer

class PollListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Poll.objects.all()
    serializer_class = PollSerializer

class PollDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
