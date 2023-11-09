from rest_framework.generics import *
from rest_framework import viewsets
from rest_framework.authentication import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import *
from .utils import *
from user.utils import send_notification
from .models import EventCategory, Event, Ticket, Bank, PayOutInfo, TicketPurchase, Withdraw
from rest_framework import status, permissions
from rest_framework.generics import *
from .serializers import *
import csv
from django.utils import timezone
from django.http import HttpResponse
from rest_framework.views import APIView
from reward.models import Reward

class EventCategoryViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = EventCategory.objects.all()
    serializer_class = EventCategorySerializer

class EventViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class TicketViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def perform_create(self, serializer:TicketSerializer) ->None:
        Reward.objects.create(user=self.request.user, medium="sell_tickets")
        serializer.save(event=self.request.user.event)  # Assuming you have an 'event' foreign key on your User model

    def perform_update(self, serializer):
        # Ensure that ticket quantities are updated correctly
        instance = serializer.instance
        if 'quantity_available' in serializer.validated_data:
            new_quantity = serializer.validated_data['quantity']
            sold_tickets = instance.total_tickets_sold()
            if new_quantity < sold_tickets:
                raise serializers.ValidationError('Quantity available cannot be less than tickets sold.')
        serializer.save()


class BankViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Bank.objects.all()
    serializer_class = BankSerializer

class PayOutInfoViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = PayOutInfo.objects.all()
    serializer_class = PayOutInfoSerializer

class WithdrawViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Withdraw.objects.all()
    serializer_class = WithdrawSerializer



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def buy_ticket(request):
    # Extract relevant data from the request (e.g., event_id, ticket_type, payment_info)
    event_id = request.data.get('event_id')
    ticket_type = request.data.get('ticket_type')
    payment_info = request.data.get('payment_info')  # Payment information (e.g., payment method, amount)

    try:
        # Retrieve the event based on event_id
        event = Event.objects.get(pk=event_id)
    except Event.DoesNotExist:
        return Response({'detail': 'Event not found'}, status=404)

    # Validate the request and perform necessary checks (e.g., check if tickets are available, validate payment)
    if not is_ticket_available(event, ticket_type):
        return Response({'detail': 'Ticket not available for this event'}, status=400)

    if not validate_payment(payment_info):
        return Response({'detail': 'Payment validation failed'}, status=400)

    # Create a TicketPurchase record
    ticket_purchase = TicketPurchase(
        user=request.user,
        event=event,
        ticket_type=ticket_type,
        payment_details=payment_info,
    )
    ticket_purchase.save()

    # Send a notification to the user about the purchase status
    if payment_successful(payment_info):
        send_notification(request.user, f"Your ticket purchase for event '{event.title}' was successful.")
        
        # Add the user to the event's attendees (assuming you have a ManyToManyField for attendees)
        event.attendees.add(request.user)
        
    else:
        send_notification(request.user, f"Your ticket purchase for event '{event.title}' failed.")

    # Send a notification to the event owner
    send_event_owner_notification(event.user, request.user, event.title, ticket_type)

    # Return a response to the user
    serializer = TicketPurchaseSerializer(ticket_purchase)
    try:
        Reward.objects.create(user=request.user, medium="buy_tickets")
    except:
        pass
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_event_promotion(request):
    event_id = request.data.get('event_id')

    try:
        event = Event.objects.get(pk=event_id)
    except Event.DoesNotExist:
        return Response({'detail': 'Event not found'}, status=404)

    # Check if the user has already requested promotion for this event
    existing_request = EventPromotionRequest.objects.filter(user=request.user, event=event).first()
    if existing_request:
        return Response({'detail': 'You have already requested promotion for this event'}, status=400)

    # Create a promotion request
    promotion_request = EventPromotionRequest(user=request.user, event=event)
    promotion_request.save()

    serializer = EventPromotionRequestSerializer(promotion_request)
    return Response(serializer.data, status=201)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsAdminUser])  # Only event organizers can access this view
def manage_event_promotion_requests(request):
    if request.method == 'GET':
        # Retrieve all promotion requests
        promotion_requests = EventPromotionRequest.objects.all()
        serializer = EventPromotionRequestSerializer(promotion_requests, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # Approve or reject a promotion request
        request_id = request.data.get('request_id')
        is_approved = request.data.get('is_approved')

        try:
            promotion_request = EventPromotionRequest.objects.get(pk=request_id)
        except EventPromotionRequest.DoesNotExist:
            return Response({'detail': 'Promotion request not found'}, status=404)

        # Update the approval status
        promotion_request.is_approved = is_approved
        promotion_request.save()

        # Send a notification to the user about the approval status
        if is_approved:
            send_notification(promotion_request.user, f"Your promotion request for '{promotion_request.event.title}' has been approved.")
        else:
            send_notification(promotion_request.user, f"Your promotion request for '{promotion_request.event.title}' has been rejected.")

        serializer = EventPromotionRequestSerializer(promotion_request)
        return Response(serializer.data)


def notify_users(event):
    # Create a notification message
    message = f"The event '{event.title}' has been deleted by the event owner."

    # Notify all users who were sticking to the event owner
    sticking_users = User.objects.filter(sticking_to=event.user)

    for user in sticking_users:
        send_notification(user, message)
    

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_event(request, event_id):
    try:
        event = Event.objects.get(pk=event_id)
    except Event.DoesNotExist:
        return Response({'detail': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)

    # Check if the user making the request is the event owner
    if request.user == event.user:
        # Get all ticket purchases for the deleted event
        ticket_purchases = TicketPurchase.objects.filter(event=event, payment_status='Successful')

        # Refund ticket fees for each purchase
        for purchase in ticket_purchases:
            refund_ticket_purchase(purchase)

        # Delete the event
        event.delete()


        # Notify users about the event deletion
        notify_users(event)

        return Response({'detail': 'Event deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    else:
        return Response({'detail': 'You do not have permission to delete this event'}, status=status.HTTP_403_FORBIDDEN)


class TicketReportAPIView(APIView):
    def get(self, request, event_id):
        # Retrieve ticket purchases for the specified event
        ticket_purchases = TicketPurchase.objects.filter(event__id=event_id)

        # Serialize the ticket purchases
        serializer = TicketPurchaseSerializer(ticket_purchases, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


def download_ticket_report(request, event_id):
    # Retrieve ticket purchases for the specified event
    ticket_purchases = TicketPurchase.objects.filter(event__id=event_id)

    # Create a CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="ticket_report_event_{event_id}.csv"'

    # Create a CSV writer
    writer = csv.writer(response)
    writer.writerow(['Attendee Name', 'Number of Tickets', 'Purchase Date', 'Price (Naira)'])

    # Populate the CSV with ticket purchase data
    for purchase in ticket_purchases:
        writer.writerow([
            purchase.user.get_full_name() or purchase.user.username,
            purchase.ticket_type,
            purchase.purchase_date.strftime('%Y-%m-%d %H:%M:%S'),
            purchase.ticket.price,  # You may need to adjust this based on your models
        ])

    return response

class EditEventAPIView(UpdateAPIView):
    queryset = Event.objects.all()
    serializer_class = UserEventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only allow event owners to edit their own events
        return Event.objects.filter(user=self.request.user)


class PastEventsAPIView(ListAPIView):
    serializer_class = EventListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter events that have already ended
        now = timezone.now()
        return Event.objects.filter(user=self.request.user, date__lt=now)

class ActiveEventsAPIView(ListAPIView):
    serializer_class = EventListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter events that are currently active
        now = timezone.now()
        return Event.objects.filter(user=self.request.user, date__gte=now)

class UpcomingEventsAPIView(ListAPIView):
    serializer_class = EventListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter events that are scheduled for the future
        now = timezone.now()
        return Event.objects.filter(user=self.request.user, date__gt=now)


class CreateWithdrawalRequestView(CreateAPIView):
    serializer_class = WithdrawalRequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Retrieve the associated ticket purchase
        ticket_purchase_id = self.request.data.get('ticket_purchase_id')
        try:
            ticket_purchase = TicketPurchase.objects.get(pk=ticket_purchase_id)
        except TicketPurchase.DoesNotExist:
            raise serializers.ValidationError('Invalid ticket purchase.')

        # Check if the user is the event owner and the ticket purchase is successful
        if ticket_purchase.event.user == self.request.user and ticket_purchase.payment_status == 'Successful':
            # Set the user making the request as the request user
            serializer.save(user=self.request.user, ticket_purchase=ticket_purchase)
        else:
            raise serializers.ValidationError('You do not have permission to create this withdrawal request.')


# class ApproveWithdrawalRequestAPIView(UpdateAPIView):
#     serializer_class = WithdrawalRequestSerializer
#     permission_classes = [permissions.IsAuthenticated, IsAdminUser]  # Adjust permissions as needed

#     def put(self, request, *args, **kwargs):
#         withdrawal_request_id = kwargs.get('pk')
#         try:
#             withdrawal_request = WithdrawalRequest.objects.get(pk=withdrawal_request_id)
#         except WithdrawalRequest.DoesNotExist:
#             return Response({'detail': 'Withdrawal request not found'}, status=status.HTTP_404_NOT_FOUND)

#         # Check if the request is already approved or rejected
#         if withdrawal_request.status != 'Pending':
#             return Response({'detail': 'Withdrawal request has already been processed'}, status=status.HTTP_400_BAD_REQUEST)

#         # Process the request (approve or reject)
#         is_approved = request.data.get('is_approved')
#         if is_approved:
#             # Perform the withdrawal and update the request status
#             # Here, you would perform the withdrawal action based on your payment gateway or logic
#             # You can add the logic here to handle the withdrawal and update the request status
#             withdrawal_request.status = 'Successful'
#             withdrawal_request.save()
            
#             # Call the function to generate and store withdrawal history
#             generate_withdrawal_history(withdrawal_request.user, withdrawal_request.amount)

#             return Response({'detail': 'Withdrawal request approved'}, status=status.HTTP_200_OK)
#         else:
#             withdrawal_request.status = 'Failed'
#             withdrawal_request.save()
#             return Response({'detail': 'Withdrawal request rejected'}, status=status.HTTP_200_OK)



class ApproveWithdrawalRequestAPIView(UpdateAPIView):
    serializer_class = WithdrawalRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]  # Adjust permissions as needed

    def put(self, request, *args, **kwargs):
        withdrawal_request_id = kwargs.get('pk')
        try:
            withdrawal_request = WithdrawalRequest.objects.get(pk=withdrawal_request_id)
        except WithdrawalRequest.DoesNotExist:
            return Response({'detail': 'Withdrawal request not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the request is already approved or rejected
        if withdrawal_request.status != 'Pending':
            return Response({'detail': 'Withdrawal request has already been processed'}, status=status.HTTP_400_BAD_REQUEST)

        # Process the request (approve or reject)
        is_approved = request.data.get('is_approved')
        if is_approved:
            # Perform the withdrawal and update the request status
            withdrawal_success = perform_withdrawal(withdrawal_request)
            
            # Call the function to generate and store withdrawal history
            generate_withdrawal_history(withdrawal_request.user, withdrawal_request.amount)

            if withdrawal_success:
                return Response({'detail': 'Withdrawal request approved'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Withdrawal request failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            withdrawal_request.status = 'Failed'
            withdrawal_request.save()
            return Response({'detail': 'Withdrawal request rejected'}, status=status.HTTP_200_OK)
