from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes, action
from poll.suggestions import suggest_polls
from rest_framework.exceptions import PermissionDenied
from django.http import Http404
from poll.utils import create_notification
from .models import *
from .serializers import *
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.authentication import *
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
# views.py
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from paystackapi.paystack import Paystack
from .models import Payment

paystack = Paystack(secret_key=settings.PAYSTACK_SECRET_KEY)


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
            create_notification(user, poll.user, f"User {user.username} has requested access to your poll: {poll.question}")

        else:
            # If the poll is public, allow the user to vote directly
            poll.voters.add(user)
        serializer.save()

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Poll
from .serializers import AccessApprovalSerializer
from rest_framework.exceptions import PermissionDenied

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
                    create_notification(self.request.user, user, f"Your access request for poll: {poll.question} has been approved.")
                else:
                    # If denied, remove the user from access requests
                    poll.access_requests.remove(user)
                    create_notification(self.request.user, user, f"Your access request for poll: {poll.question} has been denied.")
            else:
                # If the poll is public, no need for access approval
                poll.voters.add(user)
        else:
            raise PermissionDenied("You do not have permission to approve/deny access requests.")

class AccessDeclineView(generics.UpdateAPIView):
    serializer_class = AccessApprovalSerializer  # Use the same serializer as AccessApprovalView

    def perform_update(self, serializer):
        poll = serializer.validated_data['poll']
        user = serializer.validated_data['user']
        approval_status = serializer.validated_data['approval_status']

        # Check if the user is the creator of the poll
        if self.request.user == poll.user:
            if poll.type == 'Private':
                # If denied, remove the user from access requests
                poll.access_requests.remove(user)
                create_notification(self.request.user, user, f"Your access request for poll: {poll.question} has been denied.")
        else:
            raise PermissionDenied("You do not have permission to approve/deny access requests.")

class PollCreateView(generics.CreateAPIView):
    serializer_class = PollCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Set the user who is creating the poll as the poll's user field
        serializer.save(user=self.request.user)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    # Get the amount and user from the request
    user = request.user
    amount = request.data.get('amount')

    # Create a payment record
    payment = Payment(user=user, amount=amount)
    payment.save()

    # Initialize the Paystack transaction
    response = paystack.transaction.initialize(
        amount=amount * 100,  # Amount should be in kobo (multiply by 100)
        email=user.email,
        reference=str(payment.id),  # Use the payment record ID as the reference
        callback_url='your_callback_url_here',  # Specify your callback URL
    )

    # Redirect the user to the Paystack payment page
    return redirect(response['data']['authorization_url'])

@api_view(['POST'])
def paystack_callback(request):
    # Extract the reference and transaction status from the callback
    reference = request.data.get('reference')
    status = request.data.get('status')

    try:
        # Retrieve the payment record using the reference
        payment = Payment.objects.get(id=reference)
        if status == 'success':
            # Update the payment status if it was successful
            payment.status = 'success'
            payment.save()
        else:
            # Handle other status scenarios (e.g., failed)
            payment.status = 'failed'
            payment.save()
    except Payment.DoesNotExist:
        pass  # Handle the case where the payment record is not found

    # Return a JSON response to the Paystack callback
    return JsonResponse({'status': 'ok'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cast_votes(request):
    data = request.data
    user = request.user

    try:
        # Check if the user has been approved to vote
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        return Response({'detail': 'User profile not found.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Check if the user has made a successful payment
        payment = Payment.objects.filter(user=user, status='success').latest('timestamp')
    except Payment.DoesNotExist:
        return Response({'detail': 'You need to make a payment to cast votes.'}, status=status.HTTP_400_BAD_REQUEST)

    # Initialize a list to store vote-related notifications
    vote_notifications = []

    for item in data:
        poll_id = item.get('poll')
        num_votes = item.get('num_votes', 1)  # Default to 1 vote if 'num_votes' is not specified

        try:
            # Check if the user has been approved to vote in this poll
            poll = Poll.objects.get(id=poll_id)
            if user not in poll.access_requests.all():
                vote_notifications.append({'detail': f'You have not been approved to vote in poll ID {poll_id}.'})
                continue

            # Retrieve the cost of a single vote associated with the poll
            try:
                vote_cost = Vote.objects.get(user=user, poll_id=poll_id).cost
            except Vote.DoesNotExist:
                vote_notifications.append({'detail': f'This poll (ID {poll_id}) does not have a cost associated with it.'})
                continue

            # Check if the user has enough funds to cast the specified number of votes
            required_amount = vote_cost * num_votes
            if payment.amount >= required_amount:
                # Create multiple vote records
                for _ in range(num_votes):
                    vote = Vote(user=user, poll_id=poll_id, cost=vote_cost)
                    vote.save()

                # Increment the vote count in the poll
                poll.vote_count += num_votes
                poll.save()

                # Deduct the total vote cost from the user's payment
                payment.amount -= required_amount
                payment.save()

                # Create a notification for the poll owner
                message = f'User {user.username} has cast {num_votes} vote(s) on your poll: {poll.question}.'
                sender = user  # The user who cast the vote
                recipient = poll.user  # The poll owner
                notification = Notification(sender=sender, recipient=recipient, message=message)
                notification.save()

                vote_notifications.append({'detail': f'Successfully cast {num_votes} vote(s) on poll ID {poll_id}.'})
            else:
                vote_notifications.append({'detail': f'Insufficient funds to cast {num_votes} vote(s) on poll ID {poll_id}.'})
        except Poll.DoesNotExist:
            vote_notifications.append({'detail': f'Poll with ID {poll_id} not found.'})

    return Response({'vote_notifications': vote_notifications}, status=status.HTTP_200_OK)



class PollsWithVoteCountView(generics.ListAPIView):
    serializer_class = PollSerializer

    def get_queryset(self):
        # Retrieve the list of polls with their respective vote counts
        polls = Poll.objects.all()
        poll_data = []

        for poll in polls:
            # Calculate the vote count for each poll
            vote_count = poll.vote_set.count()

            # Create a dictionary with poll data and vote count
            poll_data.append({
                'poll': poll,
                'vote_count': vote_count
            })

        return poll_data

class PollResultsView(generics.RetrieveAPIView):
    serializer_class = PollResultsSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Get the poll ID from the URL
        poll_id = self.kwargs.get('poll_id')
        
        try:
            # Retrieve the poll
            poll = Poll.objects.get(id=poll_id)
            
            # Check if the user is the owner of the poll
            if poll.user == self.request.user:
                return poll
            else:
                raise PermissionDenied("You do not have permission to view this poll's results.")
        except Poll.DoesNotExist:
            raise Http404("Poll not found.")