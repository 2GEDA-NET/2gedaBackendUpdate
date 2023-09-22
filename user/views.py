from ctypes import pointer
import json  # Add this import for JSON formatting
from datetime import timezone
from django.db.models import *
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.parsers import JSONParser
from rest_framework.authentication import *
from rest_framework.viewsets import GenericViewSet
from django.db.models import Q
from chat.models import Participant
from .serializers import *
from django.middleware import csrf
from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
from user.authentication_backends import EmailOrPhoneNumberBackend
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response
from django.conf import settings
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.decorators import authentication_classes, permission_classes
from django.contrib.auth import authenticate, login
from rest_framework.views import *
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework import status, permissions
from rest_framework import generics, filters, viewsets
from rest_framework.generics import *


# Create your views here.

# Authentication APIs
@api_view(['POST'])
@permission_classes([AllowAny])
def get_auth_token(request):
    # Retrieve the user from the request or any other authentication mechanism
    user = request.user

    # Create a token for the user (e.g., during registration or login)
    token, _ = Token.objects.get_or_create(user=user)

    # Retrieve the token value
    token_value = token.key

    return Response({'token': token_value})


def get_csrf_token(request):
    token = csrf.get_token(request)
    return JsonResponse({'csrfToken': token})


@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
def create_user(request):
    if request.method == 'POST':
        data = request.data
        email = data.get('email')
        phone_number = data.get('phone_number')


        # Debugging statement: Print the email and phone number
        print(f"Email: {email}, Phone Number: {phone_number}")

        if not email and not phone_number:
            return Response({'error': 'Either email or phone number must be provided.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserRegistrationSerializer(data=data, context={'request': request})

        if email:
            # Check if a user with the provided email already exists
            if User.objects.filter(email=email).exists():
                return Response({'error': 'User with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        elif phone_number:
            # Check if a user with the provided phone number already exists
            if User.objects.filter(phone_number=phone_number).exists():
                return Response({'error': 'User with this phone number already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            try:
                user = serializer.save()
                token, created = Token.objects.get_or_create(user=user)
                token_key = token.key
                response_data = serializer.data
                response_data['token'] = token_key
                return Response(response_data, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                print(e)  # Add this line to print the IntegrityError message
                return Response({'error': 'Account details already exist.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    user = request.user

    if request.method == 'PUT':
        serializer = UserProfileUpdateSerializer(instance=user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User profile updated successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    # Validate the request data using the serializer
    serializer = UserDeletionSerializer(data=request.data)
    if serializer.is_valid():
        # Authenticate the user based on the provided password
        user = authenticate(username=request.user.username, password=serializer.validated_data['password'])
        if user is not None:
            # Logout the user to invalidate the current session
            request.auth.logout(request)
            
            # Delete the user
            user.delete()
            
            return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def delete_user_by_username_or_id(request):
    # Validate the request data using the serializer
    serializer = UserDeletionSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data.get('username')
        user_id = serializer.validated_data.get('user_id')

        if username:
            try:
                user = User.objects.get(username=username)
                user.delete()
                return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
            except User.DoesNotExist:
                return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        elif user_id:
            try:
                user = User.objects.get(pk=user_id)
                user.delete()
                return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
            except User.DoesNotExist:
                return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message": "Provide either 'username' or 'user_id' for deletion"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



def delete_account_by_username(request, username):
    # Attempt to get the user by username
    user = get_object_or_404(User, username=username)

    if request.method == 'POST':
        # Check if the request is a POST request to confirm the deletion
        user.delete()
        return JsonResponse({"message": "User deleted successfully."}, status=204)

    # If it's not a POST request, return a message indicating how to delete the user
    return JsonResponse(
        {"message": "To delete this user, send a POST request to this endpoint."},
        status=400
    )


def delete_account_by_id(request, user_id):
    # Attempt to get the user by their ID
    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        # Check if the request is a POST request to confirm the deletion
        user.delete()
        return JsonResponse({"message": "User deleted successfully."}, status=204)

    # If it's not a POST request, return a message indicating how to delete the user
    return JsonResponse(
        {"message": "To delete this user, send a POST request to this endpoint."},
        status=400
    )



# End of Authentication APIs


# User List APIs
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_users(request):
    users = User.objects.all().order_by('date_joined')  # Retrieve users sorted by date of creation

    user_data = []
    for user in users:
        user_profile = UserProfile.objects.filter(user=user).first()  # Get the user's profile

        if user_profile:
            sticker_count = user_profile.stickers.count()
            sticking_count = UserProfile.objects.filter(stickers=user_profile).count()
        else:
            sticker_count = 0
            sticking_count = 0

        user_data.append({
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'sticking_count': sticking_count,
            'sticker_count': sticker_count,
        })

    return Response(user_data, status=status.HTTP_200_OK)



class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        location_data = request.data.get('location')
        if location_data:
            # Assuming location_data is a dictionary with 'latitude' and 'longitude' keys
            latitude = location_data.get('latitude')
            longitude = location_data.get('longitude')

            # Create or update user location
            user = self.perform_create(serializer)
            user.location = pointer(longitude, latitude)  # Create a Point object from coordinates
            user.save()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


# End of User details APIs


# Sticking APIs
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stick_user(request, user_id):
    user = request.user.userprofile
    try:
        target_user = UserProfile.objects.get(pk=user_id)
    except UserProfile.DoesNotExist:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    if user != target_user:
        if user.sticking.filter(pk=user_id).exists():
            user.sticking.remove(target_user)
            # If unsticking, remove the corresponding Participant record
            Participant.objects.filter(user=user.user, sticking_to=target_user).delete()
            # Send an unstick notification
            send_notification(target_user.user, f"You were unsticked by {user.user.username}")
            return Response({"message": f"You unsticked {target_user.user.username}"})
        else:
            user.sticking.add(target_user)
            # If sticking, create a Participant record
            Participant.objects.create(user=user.user, sticking_to=target_user)
            # Send a stick notification
            send_notification(target_user.user, f"You were sticked by {user.user.username}")
            return Response({"message": f"You sticked {target_user.user.username}"})
    
    return Response({"message": "You cannot stick/unstick yourself"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_stickers(request, user_id):
    try:
        user_profile = UserProfile.objects.get(pk=user_id)
    except UserProfile.DoesNotExist:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    stickers = user_profile.stickers.all()
    serializer = UserListSerializer(stickers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_sticking(request, user_id):
    try:
        user_profile = UserProfile.objects.get(pk=user_id)
    except UserProfile.DoesNotExist:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    sticking = user_profile.sticking.all()
    serializer = UserListSerializer(sticking, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_sticking(request):
    user = request.user
    try:
        user_profile = UserProfile.objects.get(user=user)
        sticking = user_profile.sticking.all()
        sticking_data = [
            {
                'username': profile.user.username,
                'first_name': profile.user.first_name,
                'last_name': profile.user.last_name,
                'sticking_count': profile.sticking.count(),
                'sticker_count': profile.stickers.count()
            }
            for profile in sticking
        ]
        return Response(sticking_data, status=status.HTTP_200_OK)
    except UserProfile.DoesNotExist:
        return Response({"message": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_stickers(request):
    user = request.user
    try:
        user_profile = UserProfile.objects.get(user=user)
        stickers = user_profile.stickers.all()
        sticker_data = [
            {
                'username': profile.user.username,
                'first_name': profile.user.first_name,
                'last_name': profile.user.last_name,
                'sticking_count': profile.sticking.count(),
                'sticker_count': profile.stickers.count()
            }
            for profile in stickers
        ]
        return Response(sticker_data, status=status.HTTP_200_OK)
    except UserProfile.DoesNotExist:
        return Response({"message": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)


# End of sticking APIs

class UserAPIView(RetrieveAPIView):
    """
    Get user details
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


# Report Users API

@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
def report_user(request):
    if request.method == 'POST':
        serializer = ReportUserSerializer(data = request.data, context={'request': request})
        
        if serializer.is_valid():
            report = serializer.save()
            response_data = serializer.data
            return Response(response_data, status= status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Report not successful'}, status= status.HTTP_400_BAD_REQUEST)
        

class ReportUserViewSet(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = ReportedUser.objects.all()
    serializer_class = ReportedUserSerializer
    lookup_field = 'user_id'

# End of report users

class UserProfileViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


# Business APIs
class BusinessCategoryViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = BusinessCategory.objects.all()
    serializer_class = BusinessCategorySerializer

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_business_profile(request):
    if request.method == 'POST':
        # Automatically associate the user's profile with the request data
        request.data['profile'] = request.user.userprofile.pk

        serializer = BusinessProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            # Send a notification for profile creation
            send_notification(request.user, "Your business profile has been created.")

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_business_profile(request, pk):
    try:
        business_profile = BusinessProfile.objects.get(pk=pk)
    except BusinessProfile.DoesNotExist:
        return Response({'detail': 'BusinessProfile not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = BusinessProfileSerializer(business_profile, data=request.data)
        if serializer.is_valid():
            serializer.save()

            # Send a notification for profile update
            send_notification(request.user, "Your business profile has been updated.")

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BusinessAvailabilityListCreateView(generics.ListCreateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = [IsAuthenticated]
    queryset = BusinessAvailability.objects.all()
    serializer_class = BusinessAvailabilitySerializer

class BusinessAvailabilityDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = [IsAuthenticated]
    queryset = BusinessAvailability.objects.all()
    serializer_class = BusinessAvailabilitySerializer

class BusinessProfileListCreateView(generics.ListCreateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = [IsAuthenticated]
    queryset = BusinessProfile.objects.all()
    serializer_class = BusinessProfileSerializer

class BusinessProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = [IsAuthenticated]
    queryset = BusinessProfile.objects.all()
    serializer_class = BusinessProfileSerializer

class BusinessCategoryListCreateView(generics.ListCreateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = [AllowAny]
    queryset = BusinessCategory.objects.all()
    serializer_class = BusinessCategorySerializer

class BusinessCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    queryset = BusinessCategory.objects.all()
    serializer_class = BusinessCategorySerializer

# End of Business APIs

class AddressListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Address.objects.all()
    serializer_class = AddressSerializer


class PasswordChangeViewSet(GenericViewSet):
    @action(detail=False, methods=['POST'])
    def change_password(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            user = self.request.user
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']

            # Check if the old password matches the user's current password
            if user.check_password(old_password):
                user.set_password(new_password)
                user.save()
                return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid old password.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddressListCreateView(generics.ListCreateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = [IsAuthenticated]
    queryset = Address.objects.all()
    serializer_class = AddressSerializer


class VerificationCreateView(APIView):
    def post(self, request):
        serializer = VerificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerificationRetrieveView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Verification.objects.all()
    serializer_class = VerificationSerializer

# Search User
class UserSearchAPIView(APIView):
    def get(self, request):
        query = request.query_params.get('query', '')

        if query:
            # Perform a case-insensitive search across relevant fields in the database
            results = User.objects.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(username__icontains=query)
            )
            serializer = UserSerializer(results, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response([], status=status.HTTP_200_OK)


def send_notification(user, message):
    # Create a new notification
    notification = Notification(user=user, message=message)
    notification.save()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notifications(request):
    user = request.user
    notifications = Notification.objects.filter(user=user, is_read=False).order_by('-created_at')
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def block_user(request):
    # Get the user who is doing the blocking
    blocker = request.user

    # Get the user who is being blocked (you can pass this user's ID or username in the request data)
    blocked_user_id = request.data.get('blocked_user_id')

    # Check if the block already exists
    existing_block = BlockedUser.objects.filter(blocker=blocker, blocked_user__id=blocked_user_id).first()

    if existing_block:
        return Response({'detail': 'User is already blocked.'}, status=status.HTTP_400_BAD_REQUEST)

    # Create a new block
    serializer = BlockedUserSerializer(data={'blocker': blocker.id, 'blocked_user': blocked_user_id})
    if serializer.is_valid():
        serializer.save()
        return Response({'detail': 'User blocked successfully.'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_blocked_users(request):
    # Get the authenticated user
    user = request.user

    # Retrieve the list of users they have blocked
    blocked_users = BlockedUser.objects.filter(blocker=user)

    # Serialize the blocked users data
    serializer = BlockedUserSerializer(blocked_users, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)