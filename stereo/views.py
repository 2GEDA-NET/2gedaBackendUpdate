from django.shortcuts import render
from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

class PlaylistViewSet(viewsets.ModelViewSet):
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer

class SongViewSet(viewsets.ModelViewSet):
    queryset = Song.objects.all()
    serializer_class = SongSerializer

class StereoAccountRegistrationView(CreateAPIView):
    serializer_class = StereoAccountRegistrationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user_role = serializer.validated_data['user_role']
        # Set the user role based on the selected role
        if user_role == 'artist':
            serializer.save(profile=self.request.user.profile, is_artist=True, is_listener=False)
        else:
            serializer.save(profile=self.request.user.profile, is_artist=False, is_listener=True)

class StereoAccountLoginView(APIView):
    def post(self, request):
        stereo_username = request.data.get('stereo_username')
        stereo_password = request.data.get('stereo_password')
        user = authenticate(request, stereo_username=stereo_username, stereo_password=stereo_password)
        if user is not None:
            login(request, user)
            return Response({'detail': 'Login successful.'}, status=status.HTTP_200_OK)
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)