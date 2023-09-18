from django.shortcuts import render
from rest_framework import viewsets
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.authentication import *

class ConversationViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer

class MessageViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
