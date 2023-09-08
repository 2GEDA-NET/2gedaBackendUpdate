from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = '__all__'


class UserRegistrationSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone_number = serializers.CharField()  # Or use serializers.RegexField(regex=r'^\+?1?\d{9,15}$') for phone number validation
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    # phone_number = serializers.IntegerField(required = True, write_only = True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name',
                  'email', 'phone_number', 'password']

    def validate(self, validated_data):
        email = validated_data.get('email', None)
        phone_number = validated_data.get('phone_number', None)

        if not (email or phone_number):
            raise serializers.ValidationError(
                _("Enter an email or a phone number."))

        return validated_data

    def get_cleaned_data_extra(self):
        return {
            'phone_number': self.validated_data.get('phone_number', ''),
            "first_name": self.validated_data.get("first_name", ""),
            "last_name": self.validated_data.get("last_name", ""),
        }

    def create_extra(self, user, validated_data):
        user.first_name = validated_data.get("first_name")
        user.last_name = validated_data.get("last_name")
        user.save()

        phone_number = validated_data.get("phone_number")

    
        user.phone_number = phone_number
        user.save()

    def custom_signup(self, request, user):
        self.create_extra(user, self.get_cleaned_data_extra())

    def to_internal_value(self, data):
        """
        Perform the validation and conversion of input data.
        """
        if 'phone_number' in data:
            # Normalize the phone number input
            phone_number = self.fields['phone_number'].to_internal_value(
                data['phone_number'])
            data['phone_number'] = phone_number

        return super().to_internal_value(data)

    def create(self, validated_data):
        # otp = random.randint(1000, 9999)
        # otp_expiry = datetime.now() + timedelta(minutes= 10)
        phone_number = self.context.get('phone_number')

        # Create and save the User instance
        user = User.objects.create_user(
            email=validated_data.get('email'),
            password=validated_data.get('password'),
            phone_number=validated_data.get('phone_number'),
            # otp = otp,
            # otp_expiry = otp_expiry,
            # max_otp_try = settings.MAX_OTP_TRY,
        )

        # Save any additional data
        user.first_name = validated_data.get('first_name')
        user.last_name = validated_data.get('last_name')
        user.save()
        
        # TODO: call send_otp function
        # send_otp(phone_number, otp)
        return user
    

class ReportUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportedUser
        fields = ['user', 'description']

class ReportedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportedUser
        fields = '__all__'