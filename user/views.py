from ctypes import pointer
import json  # Add this import for JSON formatting
import time  # Import the time module
from django.db.models import *
from django.db.models import Q
# from otp.models import Device
# from otp.models import TOTPDevice
from twilio.rest import Client  # Import the Twilio client
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.parsers import JSONParser
from rest_framework.authentication import *
from rest_framework.viewsets import GenericViewSet
from django.db.models import Q
from business.models import BusinessDirectory
from chat.models import *
from django.contrib.auth import authenticate, login, logout
from .authentication_backends import BusinessAccountAuthBackend
from feed.models import *
from .serializers import *
from django.middleware import csrf
from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response
from django.conf import settings
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.decorators import authentication_classes, permission_classes
from django.contrib.auth import authenticate, login
from .authentication_backends import *
from rest_framework.views import *
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework import status, permissions
from rest_framework import generics, filters, viewsets
from rest_framework.generics import *
import pyotp
import secrets
import base64
import logging
from google.oauth2 import service_account
from reward.models import Reward
from .models import UserCoverImage, UserProfileImage


# Configure logging
logger = logging.getLogger(__name__)

# Create your views here.

TWILIO_ACCOUNT_SID = settings.TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN = settings.TWILIO_AUTH_TOKEN
TWILIO_PHONE_NUMBER = settings.TWILIO_PHONE_NUMBER


credentials = service_account.Credentials.from_service_account_file(
    'geda-403314-9575a2d9bab8.json', scopes=['https://www.googleapis.com/auth/gmail.send'])
email = "2gedafullstack@gmail.com"


def send_email(subject, message, to_email):
    credentials = credentials.with_subject(email)
    message = create_message("2gedafullstack@gmail.com",
                             to_email, subject, message)
    send_message(credentials, message)

# Within your view function


def generate_otp_code(secret_key, length=5):
    totp = pyotp.TOTP(secret_key, digits=length)  # Set the digits parameter
    otp_code = totp.now()

    # Log the secret key and OTP code for debugging
    logger.debug(f"Secret Key: {secret_key}")
    logger.debug(f"OTP Code: {otp_code}")

    return otp_code


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

        serializer = UserRegistrationSerializer(
            data=data, context={'request': request})

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

                # secret_key = secrets.token_urlsafe(16)
                # Generate a random 16-character secret key and encode it in Base32
                secret_key = base64.b32encode(
                    secrets.token_bytes(10)).decode('utf-8')
                user.secret_key = secret_key
                user.save()

                token, created = Token.objects.get_or_create(user=user)
                token_key = token.key

                # Generate the OTP code using the user's secret key
                otp_code = generate_otp_code(user.secret_key)

                user.otp = otp_code
                user.save()
                # Send the OTP to the user via email
                # send_mail(
                #     '2geda OTP Verification Code',
                #     f'Hi, {user.username}, Your OTP code is: {otp_code}',
                #     '2gedafullstack@gmail.com',
                #     [user.email],  # Replace with the user's email field
                #     fail_silently=False,
                # )

                # # Send the OTP to the user's phone number via Twilio
                # client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
                # message = client.messages.create(
                #     body=f'Hi, {user.username}, Your OTP code is: {otp_code}',
                #     from_=TWILIO_PHONE_NUMBER,
                #     to=phone_number,  # Replace with the user's phone_number field
                # )

                response_data = serializer.data
                response_data['token'] = token_key
                return Response(response_data, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                print(e)  # Add this line to print the IntegrityError message
                return Response({'error': 'Account details already exist.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def verify_otp(request):
    if request.method == 'POST':
        data = request.data
        otp_code = data.get('otp_code')

        if not otp_code:
            return Response({'error': 'OTP code is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the user's secret key from the authenticated user
        secret_key = request.user.secret_key

        # Get the stored OTP code from the user's model
        stored_otp = request.user.otp

        # Compare the entered OTP code with the stored OTP code
        if otp_code == stored_otp:
            # OTP code is valid
            request.user.is_verified = True
            request.user.otp_verified = True
            request.user.save()
            return Response({'message': 'OTP code is valid.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid OTP code.'}, status=status.HTTP_400_BAD_REQUEST)


# Define your view for resending OTP
@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Use the appropriate permission class
@authentication_classes([TokenAuthentication])
def resend_otp(request):
    if request.method == 'POST':
        user = request.user

        # Generate a new OTP code using the user's secret key
        otp_code = generate_otp_code(user.secret_key)

        user.otp = otp_code
        user.save()

        # Send the new OTP to the user via email
        send_mail(
            '2geda OTP Verification Code',
            f'Hi, {user.username}, Your new OTP code is: {otp_code}',
            '2gedafullstack@gmail.com',
            [user.email],  # Replace with the user's email field
            fail_silently=False,
        )

        # Send the new OTP to the user's phone number via Twilio
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f'Hi, {user.username}, Your new OTP code is: {otp_code}',
            from_=TWILIO_PHONE_NUMBER,
            # Convert user.phone_number to a string and add the plus sign
            to='+' + str(user.phone_number),
        )

        return Response({'message': 'New OTP code has been sent.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = request.data['username']
        password = request.data['password']

        print(username)
        print(password)

        if not username or not password:
            return JsonResponse({'error': 'Both username and password are required.'}, status=400)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Log the user in and return a success response
            login(request, user)
            try:
                Reward.objects.create(medium="login", user=request.user)
            except:
                pass

            return JsonResponse({'message': 'Login successful', 'token': user.auth_token.key})
        else:
            # Authentication failed; return an error response
            return JsonResponse({'error': 'Invalid login credentials'}, status=401)

    return JsonResponse({'error': 'Invalid request method'}, status=400)


class LoginAPI(APIView):
    permission_classes = []
    def post(self, request, format=None):
        username = request.data["username"]  
        password = request.data["password"] 

        if not username or not password:
            return JsonResponse({'error': 'Both username and password are required.'}, status=400)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Log the user in and return a success response
            login(request, user)
            return Response({'message': 'Login successful', 'token': user.auth_token.key})
        else:
            # Authentication failed; return an error response
            return Response({'error': 'Invalid login credentials'}, status=401)

        


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    # Get the user's token
    user = request.user
    try:
        token = Token.objects.get(user=user)
        token.delete()  # Delete the token
        return Response({'message': 'Logout successful.'}, status=status.HTTP_200_OK)
    except Token.DoesNotExist:
        return Response({'error': 'No token found for the user.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    user = request.user

    if request.method == 'PUT':
        serializer = UserProfileUpdateSerializer(
            instance=user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User profile updated successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileHasUpdatedProfileView(APIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, format=None):
        # Retrieve the user's profile based on the authenticated user
        user = self.request.user
        profile = UserProfile.objects.get(user=user)
        value = profile.has_updated_profile
        return Response({"response": value}, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    # Validate the request data using the serializer
    serializer = UserDeletionSerializer(data=request.data)
    if serializer.is_valid():
        # Authenticate the user based on the provided password
        user = authenticate(username=request.user.username,
                            password=serializer.validated_data['password'])
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
    # Retrieve users sorted by date of creation
    users = User.objects.all().order_by('date_joined')

    user_data = []
    for user in users:
        user_profile = UserProfile.objects.filter(
            user=user).first()  # Get the user's profile

        if user_profile:
            sticker_count = user_profile.stickers.count()
            sticking_count = UserProfile.objects.filter(
                stickers=user_profile).count()
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


class BusinessAccountRegistrationView(APIView):
    def post(self, request):
        serializer = BusinessAccountRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            # Get the password from the serializer data
            business_password = serializer.validated_data['business_password']
            # Hash the password using make_password
            hashed_password = make_password(business_password)
            # Update the serializer data with the hashed password
            serializer.validated_data['business_password'] = hashed_password

            business_account = serializer.save()
            # Create a token for the user
            token, created = Token.objects.get_or_create(
                user=business_account.profile.user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BusinessAccountLoginView(APIView):
    def post(self, request):
        serializer = BusinessAccountLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['business_name']
            password = serializer.validated_data['business_password']
            user = BusinessAccountAuthBackend().authenticate(request, username=username,
                                                             password=password)  # Use authenticate method
            if user is not None:
                login(request, user)
                token, created = Token.objects.get_or_create(user=user)
                return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class ManagedBusinessAccountsView(generics.ListAPIView):
    serializer_class = BusinessAccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return BusinessAccount.objects.filter(profile__user=user)


class BusinessAccountChangePasswordView(UpdateAPIView):
    serializer_class = BusinessAccountChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            user = self.get_object()
            new_password = serializer.validated_data['new_password']
            user.businessaccount.business_password = new_password
            user.businessaccount.save()
            return Response({'detail': 'Password has been changed successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            # Create a Point object from coordinates
            user.location = pointer(longitude, latitude)
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
            Participant.objects.filter(
                user=user.user, sticking_to=target_user).delete()
            # Send an unstick notification
            send_notification(target_user.user,
                              f"You were unsticked by {user.user.username}")
            return Response({"message": f"You unsticked {target_user.user.username}"})
        else:
            user.sticking.add(target_user)
            # If sticking, create a Participant record
            Participant.objects.create(user=user.user, sticking_to=target_user)
            # Send a stick notification
            send_notification(target_user.user,
                              f"You were sticked by {user.user.username}")
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
        serializer = ReportUserSerializer(
            data=request.data, context={'request': request})

        if serializer.is_valid():
            report = serializer.save()
            response_data = serializer.data
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Report not successful'}, status=status.HTTP_400_BAD_REQUEST)


class ReportUserViewSet(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = ReportedUser.objects.all()
    serializer_class = ReportedUserSerializer
    lookup_field = 'user_id'

# End of report users

class UserProfileMobile(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = UserProfile.objects.all()

    def get(self, request, format=None):
        cover_image_data = self.request.FILES['cover_image']
        profile_image_data = self.request.FILES['profile_image']
        UserCoverImage.objects.create(user=request.user, cover_image=cover_image_data)
        UserProfileImage.objects.create(user=request.user, profile_image=profile_image_data)

        return Response({'message': 'Profile updated successfully'})





class UserProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer2

    def get_object(self):
        return UserProfile.objects.get(user=self.request.user)

    def perform_update(self, serializer):
        user_profile = self.get_object()

        print("Received Data:")
        print(self.request.data)

        # Update the first name and last name fields
        user = self.request.data.get("user")
        # user_profile.user.first_name = user.first_name
            
        # user_profile.user.last_name = user.last_name

        date_of_birth = self.request.data.get('date_of_birth')
        user_profile.work = self.request.data.get('work')
        user_profile.gender = self.request.data.get('identity')
        user_profile.religion = self.request.data.get('religion')
        user_profile.custom_gender = self.request.data.get('custom_gender')
        # profile_image_data = self.request.FILES('profile_image')
        # cover_image_data = self.request.data.get('cover_image')
        
        
        # Initialize profile_image with a default value
        profile_image = None
        cover_image = None

        # cover_image_data = self.request.FILES['cover_image']

        # profile_image_data = self.request.FILES['profile_image']

        # cover_image = UserCoverImage.objects.create(user=self.request.user, cover_image=cover_image_data)

        # profile_image = UserProfileImage.objects.create(user=self.request.user, profile_image=profile_image_data)

        # Check if 'cover_image' and 'profile_image' are present in the request
        if 'cover_image' in self.request.FILES:
            cover_image_data = self.request.FILES.get('cover_image')
            cover_image = UserCoverImage.objects.create(user=self.request.user, cover_image=cover_image_data)
            user_profile.cover_image = cover_image

        if 'profile_image' in self.request.FILES:
            profile_image_data = self.request.FILES.get('profile_image')
            profile_image = UserProfileImage.objects.create(user=self.request.user, profile_image=profile_image_data)
            user_profile.media = profile_image

        if user_profile.gender == 1 or user_profile.gender == "Male":
            user_profile.gender = 'Male'
        elif user_profile.gender == 2 or user_profile.gender == "Female":
            user_profile.gender = 'Female'
        else:
            user_profile.gender = 'Rather not say'

        if user_profile.religion == 1 or user_profile.religion == 'Christainity':
            user_profile.religion = 'Christainity'
        elif user_profile.religion == 2  or user_profile.religion == 'Muslim':
            user_profile.religion = 'Muslim'
        else:
            user_profile.religion = 'Indigenous'
        

        if profile_image:
            # Assuming the field name in the serializer is 'profile_image'
            # You may need to adjust this based on your serializer
            user_profile.media = profile_image
            # Save the uploaded profile image

        if cover_image:
            # Assuming the field name in the serializer is 'cover_image'
            # You may need to adjust this based on your serializer
            user_profile.cover_image = cover_image
            # Save the uploaded cover image

        # Print the data for debugging
        print("Received Data:")
        print(f"first_name: {user_profile.user.first_name}")
        print(f"last_name: {user_profile.user.last_name}")
        print(f"work: {user_profile.work}")
        print(f"gender: {user_profile.gender}")
        print(f"custom_gender: {user_profile.custom_gender}")
        print(f"custom_gender: {user_profile.religion}")
        print(f"date_of_birth: {date_of_birth}")
        print(f"profile_image: {user_profile.media}")
        print(f"cover_image: {user_profile.cover_image}")

        # Check if date_of_birth is not empty before parsing it
        if date_of_birth:
            try:
                formatted_date = datetime.datetime.strptime(
                    date_of_birth, '%Y-%m-%d').date()
                user_profile.date_of_birth = formatted_date
                print(f"Parsed Date: {formatted_date}")
            except ValueError:
                return Response({'error': 'Invalid date format. Please use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)
        user_profile.has_updated_profile = True
        # Save the user_profile object
        user_profile.save()
        user_profile.user.save()
        print("Profile Saved")

        return Response({'message': 'Profile updated successfully'})


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

        serializer = BusinessAccountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            # Send a notification for profile creation
            send_notification(
                request.user, "Your business profile has been created.")

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def update_business_profile(request, pk):
    try:
        business_profile = BusinessAccountSerializer.objects.get(pk=pk)
    except BusinessAccountSerializer.DoesNotExist:
        return Response({'detail': 'BusinessProfile not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = BusinessAccountSerializer(
            business_profile, data=request.data)
        if serializer.is_valid():
            serializer.save()

            # Send a notification for profile update
            send_notification(
                request.user, "Your business profile has been updated.")

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


class BusinessAccountListCreateView(generics.ListCreateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = [IsAuthenticated]
    queryset = BusinessAccount.objects.all()
    serializer_class = BusinessAccountSerializer


class BusinessAccountDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = [IsAuthenticated]
    queryset = BusinessAccount.objects.all()
    serializer_class = BusinessAccountSerializer


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
    notifications = Notification.objects.filter(
        user=user, is_read=False).order_by('-created_at')
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
    existing_block = BlockedUser.objects.filter(
        blocker=blocker, blocked_user__id=blocked_user_id).first()

    if existing_block:
        return Response({'detail': 'User is already blocked.'}, status=status.HTTP_400_BAD_REQUEST)

    # Create a new block
    serializer = BlockedUserSerializer(
        data={'blocker': blocker.id, 'blocked_user': blocked_user_id})
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


class EncryptionKeyAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = self.request.user
        # Adjust this as per your user model
        user_profile = UserProfile.objects.get(user=user)
        conversations = Conversation.objects.filter(participants=user_profile)

        # Create a dictionary to store encryption keys for each conversation
        encryption_keys = {}

        for conversation in conversations:
            encryption_key = conversation.get_encryption_key()
            if encryption_key:
                encryption_keys[conversation.id] = encryption_key.decode()

        return Response(encryption_keys, status=status.HTTP_200_OK)


class SearchAPIView(generics.ListAPIView):
    serializer_class = GeneralSearchSerializer

    def get_queryset(self):
        query = self.request.query_params.get('query', '')
        # You can add more models to the search here using Q objects
        queryset1 = User.objects.filter(
            Q(field1__icontains=query) | Q(field2__icontains=query))
        queryset2 = PostMedia.objects.filter(
            Q(field3__icontains=query) | Q(field4__icontains=query))
        queryset3 = CommentMedia.objects.filter(
            Q(field5__icontains=query) | Q(field6__icontains=query))
        queryset4 = BusinessAccount.objects.filter(
            Q(field7__icontains=query) | Q(field8__icontains=query))
        queryset5 = BusinessDirectory.objects.filter(
            Q(field9__icontains=query) | Q(field10__icontains=query))
        queryset6 = Address.objects.filter(
            Q(field11__icontains=query) | Q(field12__icontains=query))

        # Combine the querysets
        # Add more as needed
        queryset = queryset1 | queryset2 | queryset3 | queryset4 | queryset5 | queryset6

        return queryset


@api_view(['POST'])
def flag_user_profile(request):
    if request.method == 'POST':
        serializer = FlagUserProfileSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get('username')

            try:
                profile_to_flag = UserProfile.objects.get(username=username)
            except UserProfile.DoesNotExist:
                return Response({'detail': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)

            # Flag the user's profile by setting the 'is_flagged' field to True
            profile_to_flag.is_flagged = True
            profile_to_flag.save()

            return Response({'detail': 'User profile flagged successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class Acct_Sync(APIView):
    permission_classes = [IsAuthenticated,]
    def post(self, request ,format=None):
        phone = request.data["phone_number"]
        user = User.objects.filter(phone_number__in=phone).values()
        return Response(list(user), status=200)