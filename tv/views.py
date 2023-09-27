from django.shortcuts import render
from rest_framework import viewsets
from .models import *
from .serializers import *

class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubsriptionSerializer

class ChannelViewSet(viewsets.ModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializers

class PlayListViewSet(viewsets.ModelViewSet):
    queryset = Playlist
    serializer_class = PlayListSerializer

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report
    serializer_class = ReportSerializer

class VideoTagViewSet(viewsets.ModelViewSet):
    queryset = VideoTag
    serializer_class = VideoTagSerializer