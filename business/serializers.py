from rest_framework import serializers
from .models import *

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class PhoneNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneNumber
        fields = '__all__'

class BusinessDirectorySerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    phone_number = PhoneNumberSerializer()

    class Meta:
        model = BusinessDirectory
        fields = '__all__'
