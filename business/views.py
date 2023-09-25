from django.shortcuts import render
from rest_framework import viewsets
from .models import BusinessDirectory, Address, PhoneNumber
from rest_framework.views import APIView
from .serializers import *
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.authentication import *
from rest_framework import status
from rest_framework.response import Response



class AddressViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

class PhoneNumberViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = PhoneNumber.objects.all()
    serializer_class = PhoneNumberSerializer

class BusinessDirectoryViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = BusinessDirectory.objects.all()
    serializer_class = BusinessDirectorySerializer


class BusinessClaimView(APIView):
    def post(self, request, format=None):
        serializer = BusinessClaimSerializer(data=request.data)
        if serializer.is_valid():
            business_id = serializer.validated_data['business_id']
            user_id = serializer.validated_data['user_id']

            # Create or retrieve the BusinessOwnerProfile
            user_profile, created = BusinessOwnerProfile.objects.get_or_create(
                user_id=user_id,
                defaults={
                    'first_name': serializer.validated_data['business_owner_first_name'],
                    'last_name': serializer.validated_data['business_owner_last_name'],
                    'phone_number': serializer.validated_data['business_owner_phone_number'],
                    'email': serializer.validated_data['business_owner_email'],
                }
            )

            # Update the claimed_by field in the BusinessDirectory
            business = BusinessDirectory.objects.get(id=business_id)
            business.claimed_by = user_profile
            business.name = serializer.validated_data['business_name']
            business.about = serializer.validated_data['business_description']
            business.email = serializer.validated_data['business_email']
            business.website = serializer.validated_data.get('business_website', '')

            # Save the updated business details
            business.save()

            # Handle business documents (e.g., license, tax ID)
            # You can add logic here to create BusinessDocument instances for each document type

            return Response({'message': 'Business claimed successfully.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
