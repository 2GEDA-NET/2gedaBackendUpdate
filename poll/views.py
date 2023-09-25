from rest_framework import generics

from poll.suggestions import suggest_polls
from .models import *
from .serializers import *
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.authentication import *
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

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


class ActivePollsView(generics.ListAPIView):
    serializer_class = PollSerializer

    def get_queryset(self):
        # Filter active polls
        return Poll.objects.filter(is_active=True)


class EndedPollsView(generics.ListAPIView):
    serializer_class = PollSerializer

    def get_queryset(self):
        # Filter polls that have ended
        return Poll.objects.filter(is_ended=True)


class ClosePollView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, poll_id, format=None):
        try:
            poll = Poll.objects.get(id=poll_id, is_active=True)
        except Poll.DoesNotExist:
            return Response({'detail': 'Poll not found or already closed.'}, status=status.HTTP_404_NOT_FOUND)

        if poll.user != request.user:
            return Response({'detail': 'You are not authorized to close this poll.'}, status=status.HTTP_403_FORBIDDEN)

        poll.is_active = False
        poll.is_ended = True
        poll.save()

        return Response({'message': 'Poll closed successfully.'}, status=status.HTTP_200_OK)
    
class PrivatePollsView(generics.ListAPIView):
    serializer_class = PollSerializer

    def get_queryset(self):
        # Filter private polls
        return Poll.objects.filter(type='Private')



class PublicPollsView(generics.ListAPIView):
    serializer_class = PollSerializer

    def get_queryset(self):
        # Filter public polls
        return Poll.objects.filter(type='Public')


class CreatePollView(generics.CreateAPIView):
    serializer_class = PollSerializer

class SearchPollsView(generics.ListAPIView):
    serializer_class = PollSerializer

    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')
        poll_type = self.request.query_params.get('type')

        queryset = Poll.objects.all()

        if keyword:
            queryset = queryset.filter(question__icontains=keyword)

        if poll_type:
            queryset = queryset.filter(type=poll_type)

        return queryset


class SuggestedPollsAPIView(generics.ListAPIView):
    serializer_class = SuggestedPollSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Retrieve the current user's profile
        user_profile = UserProfile.objects.get(user=self.request.user)

        # Get poll suggestions based on user behavior
        suggested_polls = suggest_polls(user_profile)

        return suggested_polls