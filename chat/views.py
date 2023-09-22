import datetime
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from chat.consumers import calculate_cost
from user.models import UserProfile
from rest_framework.parsers import MultiPartParser, FormParser
from .models import *
from .serializers import *
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.authentication import *
from rest_framework.generics import *
from rest_framework import status, permissions
from rest_framework.response import Response
import paystack
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import *


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    # def perform_create(self, serializer):
    #     # You can customize create behavior here, e.g., setting participants
    #     serializer.save()

    @action(detail=False, methods=['post'])
    def create_group_chat(self, request):
        # Customize the create behavior here
        # For example, set participants based on the request data
        group_name = request.data.get('group_name')
        participant_ids = request.data.get('participant_ids', [])

        if not group_name:
            return Response({'error': 'Group name is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create the conversation and set the group name
        conversation = Conversation.objects.create(group_name=group_name, is_group=True)

        # Add participants to the conversation
        participants = User.objects.filter(id__in=participant_ids)
        conversation.participants.add(*participants)

        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def assign_role(self, request, pk=None):
        conversation = self.get_object()
        participant_id = request.data.get('participant_id')
        role = request.data.get('role')

        if not participant_id or not role:
            return Response({'error': 'Participant ID and role are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            participant = User.objects.get(id=participant_id)
        except User.DoesNotExist:
            return Response({'error': 'Participant not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Ensure that the request user is the owner of the conversation or an admin
        user_role = conversation.roles.get(str(self.request.user.id))
        if user_role not in ['owner', 'admin']:
            return Response({'error': 'You do not have permission to assign roles.'}, status=status.HTTP_403_FORBIDDEN)

        # Validate the role being assigned
        if role not in ['admin', 'moderator', 'participant']:
            return Response({'error': 'Invalid role.'}, status=status.HTTP_400_BAD_REQUEST)

        # Assign the role to the participant
        conversation.roles[str(participant.id)] = role
        conversation.save()

        serializer = self.get_serializer(conversation)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def change_member_role(self, request, pk=None):
        conversation = self.get_object()
        member_id = request.data.get('member_id')
        new_role = request.data.get('new_role')

        if not member_id or not new_role:
            return Response({'error': 'Member ID and new role are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            member = User.objects.get(id=member_id)
        except User.DoesNotExist:
            return Response({'error': 'Member not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Ensure that the request user is the owner of the conversation or an admin
        user_role = conversation.roles.get(str(self.request.user.id))
        if user_role not in ['owner', 'admin']:
            return Response({'error': 'You do not have permission to change member roles.'}, status=status.HTTP_403_FORBIDDEN)

        # Validate the new role being assigned
        if new_role not in ['admin', 'moderator', 'participant']:
            return Response({'error': 'Invalid new role.'}, status=status.HTTP_400_BAD_REQUEST)

        # Change the role of the member
        conversation.roles[str(member.id)] = new_role
        conversation.save()

        serializer = self.get_serializer(conversation)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        conversation = self.get_object()
        participant_id = request.data.get('participant_id')

        if not participant_id:
            return Response({'error': 'Participant ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            participant = User.objects.get(id=participant_id)
        except User.DoesNotExist:
            return Response({'error': 'Participant not found.'}, status=status.HTTP_404_NOT_FOUND)

        conversation.participants.add(participant)
        conversation.save()

        serializer = self.get_serializer(conversation)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def remove_participant(self, request, pk=None):
        conversation = self.get_object()
        participant_id = request.data.get('participant_id')

        if not participant_id:
            return Response({'error': 'Participant ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            participant = User.objects.get(id=participant_id)
        except User.DoesNotExist:
            return Response({'error': 'Participant not found.'}, status=status.HTTP_404_NOT_FOUND)

        if participant in conversation.participants.all():
            conversation.participants.remove(participant)
            conversation.save()
            serializer = self.get_serializer(conversation)
            return Response(serializer.data)
        else:
            return Response({'error': 'Participant is not in the conversation.'}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=True, methods=['post'])
    def set_message_visibility(self, request, pk=None):
        conversation = self.get_object()
        message_id = request.data.get('message_id')
        visibility = request.data.get('visibility', 'default')

        if not message_id or visibility not in ['default', 'custom']:
            return Response({'error': 'Invalid request data.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the message based on message_id
            message = ChatMessage.objects.get(id=message_id, thread__id=conversation.id)
        except ChatMessage.DoesNotExist:
            return Response({'error': 'Message not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Ensure that the request user is a participant in the conversation
        if self.request.user not in conversation.participants.all():
            return Response({'error': 'You are not a participant in this conversation.'}, status=status.HTTP_403_FORBIDDEN)

        # Check if the user has permission to set custom visibility
        user_role = conversation.roles.get(str(self.request.user.id))

        # Participants can set custom visibility for their own messages
        if visibility == 'custom':
            if user_role not in ['owner', 'admin', 'moderator', 'participant']:
                return Response({'error': 'You do not have permission to set custom visibility.'}, status=status.HTTP_403_FORBIDDEN)

        # Set the message-specific visibility flag
        message.custom_visibility = (visibility == 'custom')
        message.save()

        serializer = self.get_serializer(conversation)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_visible_to(self, request, pk=None):
        conversation = self.get_object()
        message_id = request.data.get('message_id')
        participant_id = request.data.get('participant_id')

        if not message_id or not participant_id:
            return Response({'error': 'Invalid request data.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the message based on message_id
            message = ChatMessage.objects.get(id=message_id, thread__id=conversation.id)
        except ChatMessage.DoesNotExist:
            return Response({'error': 'Message not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Ensure that the request user is a participant in the conversation
        if self.request.user not in conversation.participants.all():
            return Response({'error': 'You are not a participant in this conversation.'}, status=status.HTTP_403_FORBIDDEN)

        # Check if the user has permission to add users who can see the message
        user_role = conversation.roles.get(str(self.request.user.id))

        # Participants can add users who can see their own messages
        if user_role not in ['owner', 'admin', 'moderator', 'participant']:
            return Response({'error': 'You do not have permission to add users who can see the message.'}, status=status.HTTP_403_FORBIDDEN)

        # Add the participant as a user who can see the message
        try:
            participant = User.objects.get(id=participant_id)
            message.visible_to.add(participant)
        except User.DoesNotExist:
            return Response({'error': 'Participant not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(conversation)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def remove_visible_to(self, request, pk=None):
        conversation = self.get_object()
        message_id = request.data.get('message_id')
        participant_id = request.data.get('participant_id')

        if not message_id or not participant_id:
            return Response({'error': 'Invalid request data.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the message based on message_id
            message = ChatMessage.objects.get(id=message_id, thread__id=conversation.id)
        except ChatMessage.DoesNotExist:
            return Response({'error': 'Message not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Ensure that the request user is a participant in the conversation
        if self.request.user not in conversation.participants.all():
            return Response({'error': 'You are not a participant in this conversation.'}, status=status.HTTP_403_FORBIDDEN)

        # Check if the user has permission to remove users who can see the message
        user_role = conversation.roles.get(str(self.request.user.id))

        # Participants can remove users who can see their own messages
        if user_role not in ['owner', 'admin', 'moderator', 'participant']:
            return Response({'error': 'You do not have permission to remove users who can see the message.'}, status=status.HTTP_403_FORBIDDEN)

        # Remove the participant from the users who can see the message
        try:
            participant = User.objects.get(id=participant_id)
            message.visible_to.remove(participant)
        except User.DoesNotExist:
            return Response({'error': 'Participant not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(conversation)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_read_only_participant(self, request, pk=None):
        conversation = self.get_object()
        message_id = request.data.get('message_id')
        participant_id = request.data.get('participant_id')

        if not message_id or not participant_id:
            return Response({'error': 'Invalid request data.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the message based on message_id
            message = ChatMessage.objects.get(id=message_id, thread__id=conversation.id)
        except ChatMessage.DoesNotExist:
            return Response({'error': 'Message not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Ensure that the request user is a participant in the conversation
        if self.request.user not in conversation.participants.all():
            return Response({'error': 'You are not a participant in this conversation.'}, status=status.HTTP_403_FORBIDDEN)

        # Check if the user has permission to add read-only participants
        user_role = conversation.roles.get(str(self.request.user.id))
        if user_role not in ['owner', 'admin', 'moderator']:
            return Response({'error': 'You do not have permission to add read-only participants.'}, status=status.HTTP_403_FORBIDDEN)

        # Add the participant as a read-only participant for the message
        try:
            participant = User.objects.get(id=participant_id)
            message.read_only_participants.add(participant)
        except User.DoesNotExist:
            return Response({'error': 'Participant not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(conversation)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def remove_read_only_participant(self, request, pk=None):
        conversation = self.get_object()
        message_id = request.data.get('message_id')
        participant_id = request.data.get('participant_id')

        if not message_id or not participant_id:
            return Response({'error': 'Invalid request data.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the message based on message_id
            message = ChatMessage.objects.get(id=message_id, thread__id=conversation.id)
        except ChatMessage.DoesNotExist:
            return Response({'error': 'Message not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Ensure that the request user is a participant in the conversation
        if self.request.user not in conversation.participants.all():
            return Response({'error': 'You are not a participant in this conversation.'}, status=status.HTTP_403_FORBIDDEN)

        # Check if the user has permission to remove read-only participants
        user_role = conversation.roles.get(str(self.request.user.id))
        if user_role not in ['owner', 'admin', 'moderator']:
            return Response({'error': 'You do not have permission to remove read-only participants.'}, status=status.HTTP_403_FORBIDDEN)

        # Remove the participant from the read-only participants of the message
        try:
            participant = User.objects.get(id=participant_id)
            message.read_only_participants.remove(participant)
        except User.DoesNotExist:
            return Response({'error': 'Participant not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(conversation)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def report_message(self, request, pk=None):
        conversation = self.get_object()
        message_id = request.data.get('message_id')

        if not message_id:
            return Response({'error': 'Invalid request data.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the message based on message_id
            message = ChatMessage.objects.get(id=message_id, thread__id=conversation.id)
        except ChatMessage.DoesNotExist:
            return Response({'error': 'Message not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Ensure that the request user is a participant in the conversation
        if self.request.user not in conversation.participants.all():
            return Response({'error': 'You are not a participant in this conversation.'}, status=status.HTTP_403_FORBIDDEN)

        # Mark the message as reported
        message.is_reported = True
        message.save()

        serializer = self.get_serializer(conversation)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def star_message(self, request, pk=None):
        conversation = self.get_object()
        message_id = request.data.get('message_id')

        if not message_id:
            return Response({'error': 'Invalid request data.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the message based on message_id
            message = ChatMessage.objects.get(id=message_id, thread__id=conversation.id)
        except ChatMessage.DoesNotExist:
            return Response({'error': 'Message not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Ensure that the request user is a participant in the conversation
        if self.request.user not in conversation.participants.all():
            return Response({'error': 'You are not a participant in this conversation.'}, status=status.HTTP_403_FORBIDDEN)

        # Mark the message as starred
        message.is_starred = True
        message.save()

        serializer = self.get_serializer(conversation)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def forward_message(self, request, pk=None):
        conversation = self.get_object()
        message_id = request.data.get('message_id')
        target_conversation_id = request.data.get('target_conversation_id')

        if not message_id or not target_conversation_id:
            return Response({'error': 'Invalid request data.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the message based on message_id
            message = ChatMessage.objects.get(id=message_id, thread__id=conversation.id)
        except ChatMessage.DoesNotExist:
            return Response({'error': 'Message not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Ensure that the request user is a participant in the conversation
        if self.request.user not in conversation.participants.all():
            return Response({'error': 'You are not a participant in this conversation.'}, status=status.HTTP_403_FORBIDDEN)

        # Ensure that the target conversation exists
        try:
            target_conversation = Conversation.objects.get(id=target_conversation_id)
        except Conversation.DoesNotExist:
            return Response({'error': 'Target conversation not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user has permission to forward messages
        user_role = conversation.roles.get(str(self.request.user.id))

        # Participants can forward messages
        if user_role not in ['owner', 'admin', 'moderator', 'participant']:
            return Response({'error': 'You do not have permission to forward messages.'}, status=status.HTTP_403_FORBIDDEN)

        # Create a new message in the target conversation with the same content
        ChatMessage.objects.create(
            thread=target_conversation,
            user=self.request.user,
            message=message.message,
            is_private=message.is_private,
            is_public=message.is_public,
            custom_visibility=message.custom_visibility,
        )

        serializer = self.get_serializer(conversation)
        return Response(serializer.data)

# Broadcast plan to be done later

# class BroadcastPlanView(APIView):
#     def get(self, request):
#         plans = BroadcastPlan.objects.all()
#         serializer = BroadcastPlanSerializer(plans, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)


# @api_view(['POST'])
# def select_broadcast_plan(request):
#     # Get the selected plan ID from the request data
#     selected_plan_id = request.data.get('plan_id')  # Assuming the plan_id is sent in the request data

#     # Now you can use the selected_plan_id to calculate the cost or perform other actions
#     cost = calculate_cost(selected_plan_id)

#     # Return a response or perform other actions as needed
#     return Response({'cost': cost})  # You can customize the response as required


# @api_view(['POST'])
# def initiate_payment(request):
#     plan_id = request.data.get('plan_id')  # ID of the selected broadcast plan
#     user = request.user  # Assuming you have user authentication in place

#     try:
#         plan = BroadcastPlan.objects.get(pk=plan_id)
#     except BroadcastPlan.DoesNotExist:
#         return Response({'error': 'Invalid plan ID'}, status=status.HTTP_400_BAD_REQUEST)

#     # Create a Paystack invoice for the selected plan
#     invoice_data = {
#         'amount': int(plan.price * 100),  # Convert price to kobo
#         'currency': 'NGN',
#         'reference': f'plan_{plan.id}_{user.id}',
#         'description': f'Purchase of {plan.name} plan',
#         'metadata': {
#             'user_id': user.id,
#             'plan_id': plan.id,
#         },
#     }

#     try:
#         invoice = paystack.invoice.create(**invoice_data)
#     except Exception as e:
#         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     # Return the payment URL to the client
#     return Response({'payment_url': invoice['data']['link']}, status=status.HTTP_200_OK)


# @csrf_exempt
# @api_view(['POST'])
# def payment_callback(request):
#     response_data = request.data

#     # Verify the payment using Paystack library
#     try:
#         payment = paystack.verify_transaction(response_data['reference'])
#     except Exception as e:
#         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     # Check if payment was successful
#     if payment.get('status') == 'success':
#         user_id = payment['metadata']['user_id']
#         plan_id = payment['metadata']['plan_id']

#         try:
#             user = User.objects.get(pk=user_id)
#             plan = BroadcastPlan.objects.get(pk=plan_id)
#         except (User.DoesNotExist, BroadcastPlan.DoesNotExist):
#             return Response({'error': 'User or plan not found'}, status=status.HTTP_404_NOT_FOUND)

#         # Update the user's account with the selected plan
#         user.selected_broadcast_plan = plan
#         user.save()

#         return Response({'message': 'Payment successful'}, status=status.HTTP_200_OK)
#     else:
#         return Response({'message': 'Payment failed'}, status=status.HTTP_400_BAD_REQUEST)


class MessageViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = ChatMessage.objects.all()
    serializer_class = MessageSerializer

class StatusViewSet(viewsets.ModelViewSet):
    queryset = LifeStyle.objects.all()
    serializer_class = LifeStyleSerializer

class ThreadListView(ListAPIView):
    serializer_class = ThreadSerializer

    def get_queryset(self):
        # Filter threads by the currently authenticated user
        return Thread.objects.by_user(user=self.request.user).prefetch_related('chatmessage_thread').order_by('timestamp')
    

class StoryUploadAPI(APIView):
    permission_classes=[IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self,request):
        story_data=request.data.get('post_images')
        serializer=LifeStyleSerializer(data={'story':story_data,'user':request.user.id})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


             

# view story

class GetStories(APIView):
    permission_classes = [IsAuthenticated]

    def get (self,request):

        follower_ids = User.objects.filter(
        user=request.user).values_list('followed_user', flat=True)
        
        follow_data = LifeStyle.objects.filter(
            Q(user__in=follower_ids) | Q(user=request.user)).order_by('-id')

        if follow_data.count() > 0:
            serializer = LifeStyleSerializer(follow_data, many=True)
            data = serializer.data

            for post in data:
                post['image_url'] = request.build_absolute_uri(
                    post['story'])
                
            
            return Response({'data': data, 'message': 'data get', 'success': 1})
        else:
            return Response({'data': 'no data available'}, status=status.HTTP_400_BAD_REQUEST)


#viewed story
class ViewedLifeStyle(APIView):
    def get(self,request,story_id):
        queryset=LifeStyle.objects.get(pk=story_id)
        queryset.status=True
        queryset.save()
        serializer=LifeStyleSerializer(queryset)

        return Response(serializer.data)
    

# story delete
class LifeStyleDelete(APIView):
    def get(self,request):
        queryset=LifeStyle.objects.all()
        serializer=LifeStyleSerializer(queryset,many=True)
        data=serializer.data

        for post in data:

            post_time_str = post['date']
            post_time_obj = datetime.strptime(
                post_time_str, '%Y-%m-%dT%H:%M:%S.%fZ')

            time_diff = datetime.now() - post_time_obj
            hours_diff = int(time_diff.total_seconds() // 3600)
            print(hours_diff)


            if hours_diff>=24:
                LifeStyle.objects.filter(id=post['id']).delete()

        return Response('LifeStyle deleted successfully')




# get single user lifestyle

class SingleUserLifeStyle(APIView):
    def get(self,request,user_id):
        queryset=LifeStyle.objects.filter(user=user_id)

        if queryset.count()>0:
            serializer=LifeStyleSerializer(queryset,many=True)
            data = serializer.data

            for post in data:
                post['image_url'] = request.build_absolute_uri(
                    post['lifestyle'])
                
            return Response(serializer.data)
        else:
            return Response({'data': 'no data available'}, status=status.HTTP_400_BAD_REQUEST)

class EncryptionKeyAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, conversation_id):
        user = self.request.user
        user_profile = UserProfile.objects.get(user=user)  # Adjust this as per your user model

        try:
            conversation = Conversation.objects.get(id=conversation_id, participants=user_profile)
            encryption_key = conversation.get_encryption_key()
            if encryption_key:
                return Response({'encryption_key': encryption_key.decode()}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Encryption key not found for this conversation.'}, status=status.HTTP_404_NOT_FOUND)
        except Conversation.DoesNotExist:
            return Response({'detail': 'Conversation not found.'}, status=status.HTTP_404_NOT_FOUND)