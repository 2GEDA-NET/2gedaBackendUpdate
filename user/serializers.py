from rest_framework import serializers
from .models import *
from django.db.models import Q
from rest_framework import serializers
from django.db.models import Q
from django.utils.translation import gettext as _

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = '__all__'


class UserRegistrationSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=False)  # Make phone_number optional
    email = serializers.EmailField(required=False)  # Make email optional
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'phone_number', 'password']

    def validate(self, validated_data):
        email = validated_data.get('email', None)
        phone_number = validated_data.get('phone_number', None)

        if not (email or phone_number):
            raise serializers.ValidationError(
                _("Enter an email or a phone number."))

        return validated_data

    def create(self, validated_data):
        email = validated_data.get('email')
        phone_number = validated_data.get('phone_number')

        # Check if either the email or phone number already exists
        if User.objects.filter(Q(email=email) | Q(username=phone_number)).exists():
            raise serializers.ValidationError(_("Account with this email or phone number already exists."))

        # Create and save the User instance
        user = User.objects.create_user(
            username = email or phone_number,  # Use email or phone_number as the username
            email=email,
            phone_number=phone_number,
            password=validated_data.get('password'),
        )

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
        fields = ['name',]

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class BusinessProfileAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['city']

class BusinessAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessAvailability
        fields = '__all__'

class BusinessProfileSerializer(serializers.ModelSerializer):
    business_availability = BusinessAvailabilitySerializer()
    address = BusinessProfileAddressSerializer()
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

        # Days of the week
        days_of_week = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']

        # Loop through days of the week and update fields
        for day in days_of_week:
            setattr(instance.business_availability, day, business_availability_data.get(day, getattr(instance.business_availability, day)))
            setattr(instance.business_availability, f'{day}_open', business_availability_data.get(f'{day}_open', getattr(instance.business_availability, f'{day}_open')))
            setattr(instance.business_availability, f'{day}_close', business_availability_data.get(f'{day}_close', getattr(instance.business_availability, f'{day}_close')))

        # Update other fields as before
        instance.year_founded = validated_data.get('year_founded', instance.year_founded)

        # Update the related Address instance
        address_data = validated_data.get('address', {})
        address = instance.address
        address.city = address_data.get('city', address.city)

        # Update the related BusinessCategory instance
        business_category_data = validated_data.get('business_category', {})
        business_category = instance.business_category
        business_category.name = business_category_data.get('name', business_category.name)

        instance.save()
        instance.business_availability.save()
        instance.address.save()
        instance.business_category.save()

        return instance

    def to_representation(self, instance):
        """
        Customize the representation of the BusinessProfile instance.
        Include sub-fields in the output.
        """
        ret = super().to_representation(instance)
        ret['business_availability'] = BusinessAvailabilitySerializer(instance.business_availability).data
        ret['address'] = BusinessProfileAddressSerializer(instance.address).data
        ret['business_category'] = BusinessCategorySerializer(instance.business_category).data
        return ret
