from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes, action
from poll.suggestions import suggest_polls
from rest_framework.exceptions import PermissionDenied
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def log_poll_view(request, poll_id):
    try:
        poll = Poll.objects.get(id=poll_id)
    except Poll.DoesNotExist:
        return Response({'detail': 'Poll not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Log the user's interaction with the poll
    PollView.objects.get_or_create(user=request.user, poll=poll)

    return Response(status=status.HTTP_200_OK)

class AccessRequestView(generics.CreateAPIView):
    serializer_class = AccessRequestSerializer  # Create a serializer for access requests

    def perform_create(self, serializer):
        poll = serializer.validated_data['poll']
        user = self.request.user
        
        # Check if the poll is private
        if poll.type == 'Private':
            # Add the user to the list of access requests
            poll.access_requests.add(user)
        else:
            # If the poll is public, allow the user to vote directly
            poll.voters.add(user)
        serializer.save()


class AccessApprovalView(generics.UpdateAPIView):
    serializer_class = AccessApprovalSerializer  # Create a serializer for access approval/denial

    def perform_update(self, serializer):
        poll = serializer.validated_data['poll']
        user = serializer.validated_data['user']
        approval_status = serializer.validated_data['approval_status']

        # Check if the user is the creator of the poll
        if self.request.user == poll.user:
            if poll.type == 'Private':
                if approval_status:
                    # If approved, add the user to the list of poll voters
                    poll.voters.add(user)
                    poll.access_requests.remove(user)
                else:
                    # If denied, remove the user from access requests
                    poll.access_requests.remove(user)
            else:
                # If the poll is public, no need for access approval
                poll.voters.add(user)
        else:
            raise PermissionDenied("You do not have permission to approve/deny access requests.")
        serializer.save()


class PollCreateView(generics.CreateAPIView):
    serializer_class = PollCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Set the user who is creating the poll as the poll's user field
        serializer.save(user=self.request.user)