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
from rest_framework import generics
from rest_framework.views import APIView
from django.conf import settings
import hashlib
import hmac
from django.conf import settings
from user.models import User  as CustomUser


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


class PaymentOnlineApi(generics.CreateAPIView):   
    permission_classes = (IsAuthenticated,)
    serializer_class = PaystackPaymentSerializer
    queryset = Ticket_Payment.objects.all()

    def perform_create(self, serializer):
        ticket_id = self.request.data["ticket_id"]
        ticket = Ticket.objects.get(pk=ticket_id)

        event = Event.objects.get(each_ticket=ticket)
        print(event.pk)
        
        serializer.validated_data["ticket"] = ticket
        serializer = serializer.save()
        event.sales.add(serializer)
        return super().perform_create(serializer)



class GetPaymentView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request,format=None):
        event = request.GET.get("event")
        amount = request.GET.get("amount")
        event = Event.objects.get(event_key=event)
        ticket = event.ticket

        headers = {
            'Authorization': f'Bearer {config}',
            'Content-Type': 'application/json',
        }

        ab = {"amount": amount, "email": request.user.email}
        data = json.dumps(ab)
        response = requests.post(
            'https://api.paystack.co/transaction/initialize', headers=headers, data=data)
        print(response.text)
        loaddata = json.loads(response.text)
        url = loaddata["data"]["authorization_url"]

        payment = Ticket_Payment.objects.create(ticket=ticket, user=request.user, amount=amount, is_initiated=True, url=url)
        response = PaystackPaymentSerializer(payment)
        return Response(response.data, status=200)



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



class EventsView(generics.ListCreateAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
    queryset = Event.objects.all()


    def perform_create(self, serializer):
        # try:
        events_category_name = self.request.data["events_category_name"]
        events_category = None
        if "events_category_image" in self.request.data:
            events_category = EventCategory.objects.create(
                name =events_category_name,
                image = self.request.FILES["events_category_image"]
            )
        else:
            events_category = EventCategory.objects.create(name=events_category_name)
        
        serializer.validated_data["category"] = events_category
        ticket_instance  = None
        instance = serializer.save()
        #Handling tickets
        ticket = self.request.data.getlist("ticket")
        for each_ticket in ticket:
            ticket_json = json.loads(each_ticket)
            category = ticket_json.get("ticket_category", None)
            price = ticket_json.get("ticket_price", None)
            quantity = ticket_json.get("ticket_quantity", None)

            is_free = ticket_json.get("is_free", None)
            ticket_instance = Ticket.objects.create(
            category=category,
            price=price,
            quantity=quantity,
            is_free = is_free
            )

            print(category)
            print(ticket_instance)
            instance = serializer.save()

            instance.each_ticket.add(ticket_instance)

        serializer.validated_data["ticket"] = ticket_instance

        instance = serializer.save()

        return super().perform_create(instance)
        # except:
        #     pass


class GetPastEvent(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        today = datetime.now()
        events = Event.objects.filter(date__lt=today).values()
        serializer = UpcomingEventSerializer(events,  many=True, context={'request': request})
        return Response(serializer.data, status=200)



class GetUpcomingEvent(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        today = datetime.now()
        events = Event.objects.filter(date__gt=today).values()
        serializer = UpcomingEventSerializer(events,  many=True, context={'request': request})
        return Response(serializer.data, status=200)


class Ticket_List(generics.ListAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    queryset = Ticket.objects.all()


class Ticket_Detail_View(generics.RetrieveAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    queryset = Ticket.objects.all()


class EventsDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
    queryset = Event.objects.all()


class EventsDestroView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request,pk,format=None):
        event = Event.objects.get(pk=pk)
        if event.user == request.user:
            event.delete()
            return Response({"response":"Successfully delete"}, status=200)

        return Response({"response":"You cant perform this action"}, status=200)
    

class EventsCategoryView(generics.ListCreateAPIView):
    permission_classes=[IsAuthenticated]
    queryset= EventCategory.objects.all()
    serializer_class = EventCategorySerializer


class EventsCategoryDetailView(generics.RetrieveDestroyAPIView):
    permission_classes=[IsAuthenticated]
    queryset= EventCategory.objects.all()
    serializer_class = EventCategorySerializer


PAYSTACK_SK = settings.PAYSTACK_SECRET_KEY
base_url = "https://api.paystack.co/"

def verify_payment( ref, *args, **kwargs):
        path = f'transaction/verify/{ref}'
        headers = {
            "Authorization": f"Bearer {PAYSTACK_SK}",
            "Content-Type": "application/json",
        }
        url = base_url + path
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            response_data = response.json()
            return response_data['status'], response_data['data']

        response_data = response.json()

        return response_data['status'], response_data['message']


class Paystack_Verification(APIView):

    def post(self, request, format=None):
        transaction_ref = request.data["transaction_ref"]

        result = verify_payment(ref=transaction_ref)

        response = {
            "status": result[0],
            "message": result[1]
        }

        return Response(response, status=200)


# class PayOnlineDone(APIView):
#     authentication_classes = []
#     permission_classes = []
#     def get(self, request, format=None):
#         print("cool")
#         a = f'{settings.PAYSTACK_SECRET_KEY}'
#         secret = bytes(a, encoding="ascii")
#         payload = request.body
#         sign = hmac.new(secret, payload, hashlib.sha512).hexdigest()
#         code = request.META.get('HTTP_X_PAYSTACK_SIGNATURE')
#         print("cool")
#         bodydata = json.loads(payload)
#         # ref = bodydata['data']['reference']
#         ref = request.GET.get("reference")

#         forwarded_for = u'{}'.format(request.META.get('HTTP_X_FORWARDED_FOR'))
     
#         whitelist = ["52.31.139.75", "52.49.173.169", "52.214.14.220"]
#         if forwarded_for is not None:
#             print("cool")
#             if code == sign:
               
#                 response = verify_payment(ref=ref)
#                 print("cool")
#                 ab = json.loads(response.text)
#                 print("cool")
#                 if (response.status_code == 200 and ab['status'] == True) and (ab["message"] == "Verification successful" and ab["data"]["status"] == "success"):
#                     user_email = ab['data']["customer"]['email']
#                     amount = ab['data']['amount']
#                     user =  User.objects.all(email=user_email)
#                     if Ticket_Payment.objects.filter(user=user).latest().DoesNotExist():
#                         Ticket_Issues.objects.create(
#                             user=user,
#                             description="Payment Initiation was False",
#                             )
                        
#                     elif Ticket_Payment.objects.filter(user=user).latest():
#                         payment_initiated = Ticket_Payment.objects.filter(user=user).latest()

#                         if payment_initiated.is_completed == False:
#                             # if payment_initiated.amount == amount:

#                             event = Event.objects.filter(ticket__pk=payment_initiated.ticket.pk)
#                             event = event.values(
#                                     "desc",
#                                     "platform",
#                                     "category",
#                                     "location",
#                                     "url",
#                                     "ticket",
#                                     "event_key",
#                                     "ticket__ticket_key",
#                                     "ticket__category",
#                                     "ticket__price",
#                                     "ticket__quantity",
#                                     "ticket__ticket_key"
#                             )
#                             return Response(list(event), status=200)
                        
#                         Ticket_Issues.objects.create(
#                             user=user,
#                             description="Payment Initiation was False",
#                             )

#                         return Response({'response':'Our payment gateway return Payment tansaction failed status {}'.format(ab["message"])}, status=200)      

#                 else:
#                     Ticket_Issues.objects.create(
#                         description="Transaction Failed",
#                         )

#                     return Response({'response':'Our payment gateway return Payment tansaction failed status {}'.format(ab["message"])}, status=200)

    
#         return Response({"response" : "Permission denied."}, status=400)


class PayOnlineDone(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self, request, format=None):

        ref = request.GET.get("reference")

        path = f'transaction/verify/{ref}'
        headers = {
            "Authorization": f"Bearer {PAYSTACK_SK}",
            "Content-Type": "application/json",
        }
        url = base_url + path
        response = requests.get(url, headers=headers)
        print("cool")
        ab = json.loads(response.text)
        message =  ab["message"]
        if (response.status_code == 200 and ab['status'] == True) and (ab["message"] == "Verification successful" and ab["data"]["status"] == "success"):
            user_email = ab['data']["customer"]['email']
            print(user_email)
            amount = ab['data']['amount']
            user =  CustomUser.objects.get(email=user_email)
            if Ticket_Payment.objects.filter(user=user) is None:
                Ticket_Issues.objects.create(
                    user=user,
                    description="Payment Initiation was False",
                    )
                
            elif Ticket_Payment.objects.filter(user=user).latest() is not None:
                payment_initiated = Ticket_Payment.objects.filter(user=user).latest()

                if payment_initiated.is_completed == False:
                    # if payment_initiated.amount == amount:

                    event = Event.objects.get(ticket__pk=payment_initiated.ticket.pk)
                    Ticket_Sales_Ticket.objects.create(
                        user=user,
                        desc= event.desc,
                        platform=event.platform,
                        category=event.category,
                        location=event.location,
                        url=event.url,
                        event_key = event.event_key,
                        ticket_key = event.ticket.ticket_key,
                        ticket_category = event.ticket.category,
                        ticket_price = event.ticket.price,
                        ticket_quantity = event.ticket.price,
                        
                    )
              

                    return Response({"response":"success"}, status=200)
                
                Ticket_Issues.objects.create(
                    user=user,
                    description="Payment Initiation was False",
                    )

                return Response({'response':'Our payment gateway return Payment tansaction failed status {}'.format(ab["message"])}, status=200)      

            else:
                Ticket_Issues.objects.create(
                    description="Transaction Failed",
                    )

                return Response({'response':'Our payment gateway return Payment tansaction failed status {}'.format(ab["message"])}, status=200)

    
        return Response({"response" : "Permission denied."}, status=400)



class Ticket_Delivery(APIView):
    permission_classes=[IsAuthenticated]
    
    def get(self, request, format=None):
        user_ticket = Ticket_Sales_Ticket.objects.filter(user=request.user).values()
        return Response(list(user_ticket), status=200)
    


#  l https://api.paystack.co/transferrecipient
# -H "Authorization: Bearer YOUR_SECRET_KEY"
# -H "Content-Type: application/json"
# -d '{ "type": "nuban", 
#       "name": "John Doe", 
#       "account_number": "0001234567", 
#       "bank_code": "058", 
#       "currency": "NGN"
#     }'
# -X POST

   

class WithdrawDetailView(generics.CreateAPIView):
    permission_classes=[IsAuthenticated]

    def post(self, request, format=None):
        user = request.user
        amount = request.data["amount"]
        bank_name = request.data["bank_name"]
        account_name  = request.data["account_name"]
        account_number = request.data["account_number"]
        account_type = request.data["account_type"]
        
        payout_instance = PayOutInfo.objects.create(
            user=user,
            bank_name =bank_name,
            account_name = account_name,
            account_number = account_number,
            account_type = account_type,
            
        )
        
        withdraw = Withdraw.objects.create(
            details=payout_instance,
            amount= amount,
            is_pending = True
        )

        withdraw = Withdraw.objects.filter(pk=withdraw.pk).values()
        return Response(list(withdraw), status=200)

        