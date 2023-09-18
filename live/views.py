from django.shortcuts import render
from rest_framework import generics
from .models import VideoSession
from .serializers import VideoSessionSerializer
from rest_framework import generics
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Video
from .serializers import VideoSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.authentication import *

class VideoUploadView(APIView):
    parser_classes = (FileUploadParser,)

    def post(self, request, *args, **kwargs):
        file_serializer = VideoSerializer(data=request.data)

        if file_serializer.is_valid():
            file_serializer.save()
            return Response(file_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VideoListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

class VideoSessionListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = VideoSession.objects.all()
    serializer_class = VideoSessionSerializer

class VideoSessionUpdateView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = VideoSession.objects.all()
    serializer_class = VideoSessionSerializer

class VideoSessionDetailView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = VideoSession.objects.all()
    serializer_class = VideoSessionSerializer