from django.shortcuts import render
from rest_framework.parsers import JSONParser
from .serializers import *
from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
from user.authentication_backends import EmailOrPhoneNumberBackend
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response
from django.conf import settings
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, login
from rest_framework.views import *
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework import status, permissions
from rest_framework import generics, filters, viewsets
from rest_framework.generics import *

# Create your views here.
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
        serializer = UserRegistrationSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            try:
                user = serializer.save()
                token = Token.objects.create(user=user)
                token_key = token.key
                response_data = serializer.data
                response_data['token'] = token_key
                return Response(response_data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({'error': 'Account details already exist.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Login(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email_or_phone = request.data.get('email_or_phone')
        password = request.data.get('password')

        if email_or_phone is None:
            return Response({'error': 'Email or phone number is required'}, status=status.HTTP_400_BAD_REQUEST)

        authenticated_user = authenticate(request, email_or_phone=email_or_phone, password=password)

        if authenticated_user is not None:
            token, created = Token.objects.get_or_create(user=authenticated_user)
            return Response({'success': 'Login successful', 'token': token.key}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid email/phone number or password'}, status=status.HTTP_401_UNAUTHORIZED)



class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, methods=["PATCH"])
    def verify_otp(self, request, pk=None):
        instance = self.get_object()

        if (
            not instance.is_active
            and instance.otp == request.data.get("otp")
            and instance.otp_expiry
            and timezone.now() < instance.otp_expiry
        ):
            instance.is_active = True
            instance.otp_expiry = None
            instance.max_otp_try = settings.MAX_OTP_TRY
            instance.otp_max_out = None
            instance.save()
            send_otp(instance.mobile, otp)
            return Response(
                "Successfully verified the user.", status=status.HTTP_200_OK
            )
        return Reponse(
            "User active or Please enter the correct otp.", status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["PATCH"])
    def regenerate_otp(self, request, pk=None):
        instance = self.get_object()

        if int(instance.max_otp_try) == 0 and timezone.now() < instance.otp_max_out:
            return Response(
                "Max OTP try reached, try after an hour.",
                status=status.HTTP_400_BAD_REQUEST
            )
            otp = random.randInt(1000, 9000)
            otp_expiry = timezone.now() + datetime.timedelta(minutes=10)
            max_otp_try = int(instance.max_otp_try) - 1

            instance.otp = otp
            instance.otp_expiry = otp_expiry
            instance.max_otp_try = max_otp_try

            if max_otp_try == 0:
                instance.otp_max_out = timezone.now() + datetime.timedelta(hour=1)
            elif max_otp_try == 1:
                instance.max_otp_try = settings.MAX_OTP_TRY
            else:
                instance.otp_max_out = None
                instance.max_otp_try = max_otp_try
            instance.save()

            send_otp(instance.mobile, otp)

            return Response("Successfully re-generated the new OTP", status=status.HTTP_200_OK)


class UserAPIView(RetrieveAPIView):
    """
    Get user details
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


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
    queryset = ReportedUser.objects.all()
    serializer_class = ReportedUserSerializer
    lookup_field = 'pk'
        
    def get_object(self):
        return self.request.user
