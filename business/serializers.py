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

class BusinessClaimSerializer(serializers.Serializer):
    business_id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    business_name = serializers.CharField(max_length=250)
    business_description = serializers.CharField(max_length=1000)
    business_email = serializers.EmailField()
    business_website = serializers.URLField(allow_blank=True, required=False)
    # Add fields for other information and documents