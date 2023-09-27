from django.shortcuts import render
from rest_framework import viewsets
from .models import *
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from .serializers import *
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from rest_framework.generics import CreateAPIView
from rest_framework import generics
from pydub import AudioSegment
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .filters import *



class SongSearchView(generics.ListAPIView):
    queryset = Song.objects.all()
    serializer_class = SongSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = SongFilter
    search_fields = ['title', 'genre']

    # You can add more filter fields if needed

class ArtistSearchView(generics.ListAPIView):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ArtistFilter
    search_fields = ['name']



class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

class PlaylistViewSet(viewsets.ModelViewSet):
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # Update the playlist count when a new playlist is created
            request.user.musicprofile.increment_playlist_count()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        # Update the playlist count when a playlist is deleted
        request.user.musicprofile.decrement_playlist_count()
        return Response(status=status.HTTP_204_NO_CONTENT)

class SongViewSet(viewsets.ModelViewSet):
    queryset = Song.objects.all()
    serializer_class = SongSerializer

class ArtistViewSet(viewsets.ModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer

class UserDownloadsList(generics.ListAPIView):
    serializer_class = DownloadRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DownloadRecord.objects.filter(user=self.request.user)

class StereoAccountRegistrationView(CreateAPIView):
    serializer_class = StereoAccountRegistrationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user_role = serializer.validated_data['user_role']
        # Set the user role based on the selected role
        if user_role == 'artist':
            serializer.save(profile=self.request.user.userprofile, is_artist=True, is_listener=False)
        else:
            serializer.save(profile=self.request.user.userprofile, is_artist=False, is_listener=True)

class StereoAccountLoginView(APIView):
    def post(self, request):
        stereo_username = request.data.get('stereo_username')
        stereo_password = request.data.get('stereo_password')
        user = authenticate(request, stereo_username=stereo_username, stereo_password=stereo_password)
        if user is not None:
            login(request, user)
            return Response({'detail': 'Login successful.'}, status=status.HTTP_200_OK)
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class QuickPickSongsAPIView(generics.ListAPIView):
    queryset = Song.objects.filter(is_quick_pick=True)
    serializer_class = SongSerializer

class TopAlbumsAPIView(generics.ListAPIView):
    queryset = Album.objects.filter(is_top_album=True)  # Query to get "Top Albums"
    serializer_class = AlbumSerializer


class BigHitAPIView(generics.ListAPIView):
    queryset = Song.objects.filter(is_big_hit=True)  # Query to get "Top Albums"
    serializer_class = SongSerializer

def download_song(request, song_id):
    song = get_object_or_404(Song, pk=song_id)
    audio_file = song.audio_file

    response = FileResponse(open(audio_file.path, 'rb'))
    # Set the Content-Disposition header to include the song title as the filename
    response['Content-Disposition'] = f'attachment; filename="{song.title}.mp3"'

    # Log the download in the DownloadedRecord model if the user is authenticated
    if request.user.is_authenticated:
        DownloadRecord.objects.create(user=request.user, song=song)

    return response

def stream_song(request, song_id):
    song = get_object_or_404(Song, pk=song_id)

    # Increment the stream count for the song
    song.stream_count += 1
    song.save()

    # Open the audio file and convert it to the desired format (e.g., MP3)
    audio = AudioSegment.from_file(song.audio_file.path, format="mp3")

    # Set the response headers for audio streaming
    response = HttpResponse(content_type="audio/mpeg")
    response['Content-Disposition'] = f'inline; filename="{song.title}.mp3"'

    # Stream the audio data to the client
    audio.export(response, format="mp3")

    return response


class SongsByAlbumAPIView(generics.ListAPIView):
    serializer_class = SongSerializer

    def get_queryset(self):
        album_name = self.kwargs['album_name']
        return Song.objects.filter(album__title=album_name)

class SongsByGenreAPIView(generics.ListAPIView):
    serializer_class = SongSerializer

    def get_queryset(self):
        genre_name = self.kwargs['genre_name']
        return Song.objects.filter(genre__name=genre_name)

class PlaylistCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the user's profile and retrieve the playlist count
        user_profile = request.user.musicprofile
        playlist_count = user_profile.playlist_count

        # Serialize the playlist count and return it as a response
        serializer = PlaylistCountSerializer({'playlist_count': playlist_count})
        return Response(serializer.data, status=status.HTTP_200_OK)

class LikeDislikeSongView(APIView):
    def post(self, request, song_id):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Get the song object
        try:
            song = Song.objects.get(pk=song_id)
        except Song.DoesNotExist:
            return Response({'detail': 'Song not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user has already liked/disliked the song
        user_preference, created = UserSongPreference.objects.get_or_create(
            user=request.user.profile,
            song=song,
        )

        # Determine the interaction type (like or dislike) based on the request data
        is_like = request.data.get('is_like', True)  # Default to like if not specified

        # Update the user's preference
        user_preference.is_like = is_like
        user_preference.save()

        return Response({'detail': 'Song preference updated successfully.'}, status=status.HTTP_200_OK)


class TopSongsByArtistAPIView(generics.ListAPIView):
    serializer_class = SongSerializer

    def get_queryset(self):
        artist_name = self.kwargs['artist_name']  # Assuming you pass the artist name as a URL parameter
        return Song.objects.filter(artist__name=artist_name, is_top_track=True)

class SongUploadView(generics.CreateAPIView):
    queryset = Song.objects.all()
    serializer_class = SongUploadSerializer

class IsArtistPermission(BasePermission):
    def has_permission(self, request, view):
        # Check if the user is an artist (assuming 'is_artist' is a field in UserProfile)
        return request.user.profile.is_artist

class ArtistSongUploadView(generics.CreateAPIView):
    queryset = Song.objects.all()
    serializer_class = ArtistSongUploadSerializer
    permission_classes = [IsAuthenticated, IsArtistPermission]

class DeleteSongView(generics.DestroyAPIView):
    queryset = Song.objects.all()
    permission_classes = [IsAuthenticated, IsArtistPermission]

    def perform_destroy(self, instance):
        # Ensure that only the artist who uploaded the song can delete it
        if self.request.user.profile == instance.album.artist:
            instance.delete()
        else:
            raise PermissionDenied("You do not have permission to delete this song.")


class StreamCountViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Song.objects.all()
    serializer_class = StreamCountSerializer  # Create a serializer for this view

    def list(self, request, *args, **kwargs):
        # Create a dictionary with song titles as keys and stream counts as values
        stream_counts = {song.title: song.stream_count for song in self.queryset}

        return Response(stream_counts)