from django.shortcuts import render
from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework.views import APIView
from django.http import FileResponse, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from rest_framework.decorators import action

class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        if query:
            return Video.objects.filter(
                title__icontains=query
            )
        return Video.objects.all()


def download_movie(request, video_id):
    video = get_object_or_404(Video, pk=video_id)

    # Increment the download count
    video.download_count += 1
    video.save()

    # Define the full path to the movie file
    movie_file_path = video.video_file.path

    # Serve the file for download using Django's FileResponse
    response = FileResponse(open(movie_file_path, 'rb'))

    # Set the content type for the response (e.g., video/mp4 for MP4 files)
    response['Content-Type'] = 'video/mp4'

    # Set the Content-Disposition header to suggest a filename to the user
    response['Content-Disposition'] = f'attachment; filename="{video.title}.mp4"'

    return response


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer


def like_video(request, video_id):
    video = get_object_or_404(Video, pk=video_id)
    user = request.user  # Assuming you're using authentication

    if request.method == 'POST':
        # Check if the user has already liked the video
        liked = Like.objects.filter(user=user, video=video).exists()

        if liked:
            # User has already liked the video, so unlike it
            Like.objects.filter(user=user, video=video).delete()
            liked = False
        else:
            # User has not liked the video, so like it
            Like.objects.create(user=user, video=video, is_like=True)
            liked = True

        # Return the updated like status and like count
        like_count = Like.objects.filter(video=video, is_like=True).count()
        dislike_count = Like.objects.filter(video=video, is_like=False).count()
        data = {
            'liked': liked,
            'like_count': like_count,
            'dislike_count': dislike_count,
        }
        return JsonResponse(data)


class VideoUploadViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        # Associate the uploaded video with the user's channel
        user_channel = self.request.user.channel  # Assuming there's a one-to-one relationship between users and channels
        serializer.save(channel=user_channel)

    def create(self, request, *args, **kwargs):
        # Override the create method to add custom response data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {'message': 'Video uploaded successfully', 'video_id': serializer.data['id']},
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class VideoDeletionViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

    @action(detail=True, methods=['post'])
    def delete_video(self, request, pk=None):
        video = self.get_object()
        # Ensure the user can only delete their own videos
        if request.user == video.channel.owner:
            video.delete()
            return Response({'message': 'Video deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'You do not have permission to delete this video'}, status=status.HTTP_403_FORBIDDEN)


class VideoHidingViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

    @action(detail=True, methods=['post'])
    def hide_video(self, request, pk=None):
        video = self.get_object()
        # Ensure the user can only hide/unhide their own videos
        if request.user == video.channel.owner:
            video.hidden = not video.hidden
            video.save()
            return Response({'message': 'Video hidden/unhidden successfully'}, status=status.HTTP_200_OK)
        return Response({'detail': 'You do not have permission to hide/unhide this video'}, status=status.HTTP_403_FORBIDDEN)


class VideoHiddenListViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = VideoSerializer

    def get_queryset(self):
        # Retrieve all hidden videos for the authenticated user
        return Video.objects.filter(channel__owner=self.request.user, hidden=True)

class VideoSchedulingViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

    @action(detail=True, methods=['post'])
    def schedule_upload(self, request, pk=None):
        video = self.get_object()
        scheduled_date_time = request.data.get('scheduled_date_time')

        # Check if the user can schedule the video
        if request.user == video.channel.owner:
            # Set the scheduled date and time for the video
            video.scheduled_date_time = scheduled_date_time
            video.save()
            return Response({'message': 'Video scheduled for upload'}, status=status.HTTP_200_OK)
        return Response({'detail': 'You do not have permission to schedule this video'}, status=status.HTTP_403_FORBIDDEN)

class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubsriptionSerializer


class ChannelViewSet(viewsets.ModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializers
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class PlayListViewSet(viewsets.ModelViewSet):
    queryset = Playlist
    serializer_class = PlayListSerializer


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report
    serializer_class = ReportSerializer


class VideoTagViewSet(viewsets.ModelViewSet):
    queryset = VideoTag
    serializer_class = VideoTagSerializer


class TVAccountRegistrationView(CreateAPIView):
    serializer_class = TVAccountRegistrationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(profile = self.request.user.userprofile)

class TVAccountLoginView(APIView):
    def post(self, request):
        tv_username = request.data.get('tv_username')
        tv_password = request.data.get('tv_password')
        user = authenticate(request, tv_username = tv_username, tv_password = tv_password)

        if user is not None:
            login(request, user)
            return Response({'detail': 'Login Successful.'}, status=status.HTTP_200_OK)
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)