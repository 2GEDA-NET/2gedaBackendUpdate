from rest_framework import status, generics


from rest_framework.response import Response


from rest_framework.viewsets import ModelViewSet


from .serializers import *
from core.models import UserModel, OtpReceiver
from django.contrib.auth import authenticate
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import OtpReceiver
from django.core.mail import send_mail
from rest_framework.decorators import action
from . otp_sender import *
from django.db import transaction
from rest_framework.views import APIView
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from datetime import timedelta

import hashlib

from django.views.decorators.csrf import csrf_protect

from ctypes import pointer

from django.utils.decorators import method_decorator

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

from business.models import BusinessDirectory

from chat.models import *

from django.contrib.auth import authenticate, login, logout

from .authentication_backends import BusinessAccountAuthBackend

from feed.models import *

from django.middleware import csrf

from rest_framework.views import APIView

from rest_framework.authtoken.models import Token

from django.views.decorators.csrf import csrf_exempt

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






class RegisterView(ModelViewSet):
    serializer_class = UserRegistrationSerializer
    queryset = UserModel.objects.all()
    http_method_names = ['post']

    def get_serializer_context(self):
        return {'request': self.request}

    def create(self, request, *args, **kwargs):
        data = request.data
        phone = data.get('phone')
        email = data.get('email')
        username = data.get('username')

        try:
            if UserModel.objects.filter(username=username).exists():
                return Response({'status': 'fail', 'message': 'Username already exist'}, status=status.HTTP_400_BAD_REQUEST)
                
            # '''Check if a user with the given phone number or email already exists.
            # We are checking for the two since we know that every user will always have one of the two, as in
            # blank mobile number or email at the point of registration'''

            user = None

            if UserModel.objects.filter(Q(phone=phone) | Q(email=email)).exists():
                user_phone = UserModel.objects.filter(phone=phone).first()
                user_email = UserModel.objects.filter(email=email).first()

                phone = user_phone.phone
                email = user_email.email
            
                if phone:

                    return Response({'status': 'fail', 'message': 'Mobile number already exist'}, status=status.HTTP_400_BAD_REQUEST)

                elif email:
                    # print(email)
                    return Response({'status': 'fail', 'message': 'Email already exist'}, status=status.HTTP_400_BAD_REQUEST)
            
                elif not phone or email:


                    raise ValueError('This field is required!')

            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            if email:

                registration_send_otp(user_input=email, is_email=True)
                user = UserModel.objects.get(email=email)
                user_otp = OtpReceiver.objects.get(user=user)
                message = f"OTP Successfully sent to {email}"
                return Response({'message': message}, status=status.HTTP_200_OK)

            elif phone:
                registration_send_otp(user_input=phone, is_email=False)
                user = UserModel.objects.get(phone=phone)
                message = f"OTP Successfully sent to {phone}"
                print(message)

                return Response({'message': message}, status=status.HTTP_200_OK)
            else:

                raise ValueError('Email or phone number is required for OTP sending')
            
                # user.registration_timestamp = timezone.now()
            user_otp = OtpReceiver.objects.get(user=user)
            if not user_otp.otp.exists():
                user.delete()
                return Response({'message': 'Please Restart your Registration Process.'}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as error_message:
            return Response({'status': 'fail', 'message': str(error_message)}, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    @action(detail=False, methods=['post'], url_path='resend-otp')
    def resend_otp(self, request):
        data = request.data
        phone = data.get('phone')
        email = data.get('email')
        try:
            # Retrieve the user from the database
            user = None
            if UserModel.objects.filter(phone=phone).exists():
                user = UserModel.objects.get(phone=phone)
            elif UserModel.objects.filter(email=email).exists():
                user = UserModel.objects.get(email=email)

            if not user:

                return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            # Check if the user has already verified OTP

            if user.is_verified:

                return Response({'message': 'User has already been verified'}, status=status.HTTP_400_BAD_REQUEST)

            if "@" in email:

                registration_send_otp(user_input=email, is_email=True)
            else:
                registration_send_otp(user_input=phone, is_email=False)

            user.save()
            return Response({'message': 'OTP resent successfully'}, status=status.HTTP_200_OK)

        except Exception as error_message:

            return Response({'status': 'fail', 'message': str(error_message)}, status=status.HTTP_400_BAD_REQUEST)


class VerifyOtpView(generics.UpdateAPIView):

    serializer_class = VerifyOtpUserSerializer

    queryset = OtpReceiver
    def update(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            otp = serializer.validated_data["otp"]
            user_submitted_value = otp  
            otp = hashlib.sha256(user_submitted_value.encode('utf-8')).hexdigest()

            # Retrieve the user associated with this OTP
            otp_receiver = OtpReceiver.objects.get(otp=otp)
            user = otp_receiver.user
            # Check if the token is still valid
            expiration_time = otp_receiver.created_at + timedelta(minutes=67)

            if timezone.now() > expiration_time:

                return Response({"message": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)

            # Mark the user as verified
            user.is_verified = True
            user.save()
            # Delete the OTP receiver record

            otp_receiver.delete()
            token, created = Token.objects.get_or_create(user=user)
            return Response({'message': f'Account verified successfully. Welcome {user.username}', 'token': token.key}, status=status.HTTP_200_OK)
        except Exception as error_message:
            return Response({'status': 'fail', 'message': str(error_message)}, status=status.HTTP_400_BAD_REQUEST)







@method_decorator(csrf_protect, name='dispatch')
class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    queryset = UserModel.objects.all()
    def get_serializer_context(self):

        return {'request': self.request}

    def post(self, request):
        data = request.data
        username = data.get('username')
        email = data.get('email')
        phone = data.get('phone')
        password = data.get('password')

        if not (email or username):
            return Response({'status': 'Fail', 'message': 'Either email or username is required'}, status=status.HTTP_400_BAD_REQUEST)

        user = None
        if email:
            user = UserModel.objects.filter(email=email).first()
        elif username:
            user = UserModel.objects.filter(username=username).first()
        if user is None or not user.check_password(password):

            return Response({'status': 'Fail', 'message': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate or retrieve the user's authentication token
        token, created = Token.objects.get_or_create(user=user)
        serializer = self.serializer_class(user)
        return Response({'status': f'Login successful. Welcome {user.username}', 'token': token.key})

@method_decorator(csrf_protect, name='dispatch')

class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        # Delete the user's token to log them out
        request.auth.delete()
        return Response({"status": "Logout successful", "message": "You have been logged out"}, status=status.HTTP_200_OK)



# @method_decorator(csrf_protect, name='dispatch')
class PasswordResetRequestView(ModelViewSet):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = PasswordResetRequestSerializer
    # queryset = UserModel.objects.all()

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        phone = serializer.validated_data.get("phone")

        try:

            # Ensure the email or phone is the same as the request.user details

            if (email and email != request.user.email) or (phone and phone != request.user.phone):
                raise PermissionDenied("You can only reset the password for your own account.")
            if email:

                    password_send_otp(user_input=email, is_email=True)
                    user = UserModel.objects.get(email=email)
                    message = f"OTP Successfully sent to {email}"
                    return Response({'message': message}, status=status.HTTP_200_OK)

            elif phone:
                password_send_otp(user_input=phone, is_email=False)
                user = UserModel.objects.get(phone=phone)
                message = f"OTP Successfully sent to {phone}"
                print(message)
                return Response({'message': message}, status=status.HTTP_200_OK)

            else:
                raise ValueError('Email or phone number is required for OTP sending')  
        except Exception as error_message:


            return Response({'status': 'fail', 'message': str(error_message)}, status=status.HTTP_400_BAD_REQUEST)


    @transaction.atomic
    @action(detail=False, methods=['post'], url_path='password-reset-resend-otp')
    def password_resend_otp(self, request):
        try:
            user = request.user  # Get the user from the request
            if "@" in user.email:
                password_send_otp(user_input=user.email, is_email=True)

            else:

                password_send_otp(user_input=user.phone, is_email=False)

            user.save()


            return Response({

                    'message': 'OTP resent successfully'

                    }, status=status.HTTP_200_OK)

        except Exception as error_message:

            return Response({'status': 'fail', 'message': str(error_message)}, status=status.HTTP_400_BAD_REQUEST)



@method_decorator(csrf_protect, name='dispatch')

class PasswordResetConfirmView(generics.UpdateAPIView):


    authentication_classes = [TokenAuthentication]


    permission_classes = [IsAuthenticated]


    serializer_class = PasswordResetConfirmSerializer



    def update(self, request, *args, **kwargs):


        serializer = self.get_serializer(data=request.data)


        serializer.is_valid(raise_exception=True)


        otp = serializer.validated_data["otp"]

        user_submitted_value = otp  

        otp = hashlib.sha256(user_submitted_value.encode('utf-8')).hexdigest()



        try:


            reset_request = OtpReceiver.objects.get(otp=otp)


        except OtpReceiver.DoesNotExist:


            return Response({"message": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)



        # Check if the token is still valid


        expiration_time = reset_request.created_at + timedelta(seconds=4900)


        if timezone.now() > expiration_time:


            return Response({"message": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)



        # Allow the user to reset their password


        new_password = serializer.validated_data["new_password"]


        user = reset_request.user


        user.set_password(new_password)


        user.save()



        # Delete the reset request


        reset_request.delete()



        return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)



@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def update_user_profile(request):

    user = request.user


    if request.method == 'PUT':

        serializer = UserProfileUpdateSerializer(
            instance=user, data=request.data)
        user_updated = UserProfile.objects.get(user=user)

        if serializer.is_valid(raise_exception=True):
            user_updated.has_updated_profile = True
            # confirm_message = 'True'
            serializer.save()
            return Response({"message": "User profile updated successfully", 'has_updated_profile': user_updated.has_updated_profile}, status=status.HTTP_200_OK )
        else:
            # confirm_message = 'False'
            return Response({'message': serializer.errors, 'has_updated_profie': f'{user_updated.has_updated_profile}'}, status=status.HTTP_400_BAD_REQUEST )

        

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

                user = UserModel.objects.get(username=username)
                user.delete()

                return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

            except User.DoesNotExist:

                return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        elif user_id:

            try:

                user = UserModel.objects.get(pk=user_id)
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

    user = get_object_or_404(UserModel, username=username)


    if request.method == 'POST':

        # Check if the request is a POST request to confirm the deletion
        user.delete()

        return JsonResponse({"message": "User deleted successfully."}, status=204)


    # If it's not a POST request, return a message indicating how to delete the user

    return JsonResponse(

        {"message": "To delete this user, send a POST request to this endpoint."},

        status=400
    )



# # End of Authentication APIs



# User List APIs

@api_view(['GET'])

@permission_classes([IsAuthenticated])

def list_users(request):

    # Retrieve users sorted by date of creation

    users = UserModel.objects.all().order_by('date_joined')


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



@method_decorator(csrf_protect, name='dispatch')

class BusinessAccountRegistrationView(APIView):

    def post(self, request):

        serializer = BusinessAccountRegistrationSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):

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

            user = BusinessAccountAuthBackend().authenticate(request, username=username, password=password)  # Use authenticate method

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

        serializer = self.get_serializer(data=request.data, context={'request': request})

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

    queryset = UserModel.objects.all()

    serializer_class = UserRegistrationSerializer


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

    queryset = UserModel.objects.all()

    serializer_class = UserRegistrationSerializer

    permission_classes = (permissions.IsAuthenticated,)


    def get_object(self):

        return self.request.user



# Report Users API


@api_view(['POST'])

# @csrf_exempt

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

            results = UserModel.objects.filter(

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

        queryset1 = UserModel.objects.filter(

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

        if serializer.is_valid(raise_exception=True):

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