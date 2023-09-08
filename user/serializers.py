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

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class BusinessCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessCategory
        fields = '__all__'

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class BusinessAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessAvailability
        fields = '__all__'


class BusinessProfileSerializer(serializers.ModelSerializer):
    business_availability = BusinessAvailabilitySerializer()
    address = AddressSerializer()
    business_category = BusinessCategorySerializer()  # Include the BusinessCategorySerializer

    class Meta:
        model = BusinessProfile
        fields = '__all__'

    def create(self, validated_data):
        business_availability_data = validated_data.pop('business_availability')
        address_data = validated_data.pop('address')
        business_category_data = validated_data.pop('business_category')  # Extract business category data

        business_availability = BusinessAvailability.objects.create(**business_availability_data)
        address = Address.objects.create(**address_data)
        business_category = BusinessCategory.objects.create(**business_category_data)  # Create business category

        business_profile = BusinessProfile.objects.create(
            business_availability=business_availability,
            address=address,
            business_category=business_category,  # Assign business category
            **validated_data
        )

        return business_profile

    def update(self, instance, validated_data):
        business_availability_data = validated_data.get('business_availability', {})
        address_data = validated_data.get('address', {})
        business_category_data = validated_data.get('business_category', {})  # Extract business category data

        instance.role = validated_data.get('role', instance.role)
        instance.image = validated_data.get('image', instance.image)
        instance.year_founded = validated_data.get('year_founded', instance.year_founded)

        # Update the related BusinessAvailability instance
        business_availability = instance.business_availability
        business_availability.always_available = business_availability_data.get('always_available', business_availability.always_available)
        business_availability.sunday = business_availability_data.get('sunday', business_availability.sunday)
        business_availability.monday = business_availability_data.get('monday', business_availability.monday)
        # Update other day fields in a similar manner

        # Update the related Address instance
        address = instance.address
        address.country = address_data.get('country', address.country)
        address.city = address_data.get('city', address.city)
        address.street_address = address_data.get('street_address', address.street_address)
        address.apartment_address = address_data.get('apartment_address', address.apartment_address)
        # Update other address fields in a similar manner

        # Update the related BusinessCategory instance
        business_category = instance.business_category
        business_category.name = business_category_data.get('name', business_category.name)
        business_category.desc = business_category_data.get('desc', business_category.desc)

        instance.save()
        business_availability.save()
        address.save()
        business_category.save()

        return instance
