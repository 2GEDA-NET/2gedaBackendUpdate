from rest_framework import serializers
from .models import *
from django.db.models import Q
from rest_framework import serializers
from django.db.models import Q
from django.utils.translation import gettext as _
from django.contrib.auth.hashers import check_password
from typing import Any


class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ["id","email","is_business","is_personal","is_admin","username","phone_number","is_verified","last_seen"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=False)  # Make phone_number optional
    email = serializers.EmailField(required=False)  # Make email optional
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'phone_number', 'username','password']

    def validate(self, validated_data):
        error = {}
        email = validated_data.get('email')
        phone_number = validated_data.get('phone_number')

        if not email and not phone_number:
            error["error"] = "Enter an email or a phone number"
            raise serializers.ValidationError(error)

        return validated_data


    def create(self, validated_data):
        email = validated_data.get('email')
        phone_number = validated_data.get('phone_number')
        username = validated_data.get('username')
        
        # Debugging statement: Print the email and phone number
        print(f"Creating user with Email: {email}, Phone Number: {phone_number}")

        # Create and save the User instance
        user = User.objects.create_user(
            username = username,
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

# class UserProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserProfile
#         fields = '__all__'

class BusinessCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessCategory
        fields = ['name',]

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class CurrentCityAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address  # Replace 'Address' with the actual name of your Address model
        fields = ('current_city',)

class BusinessAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessAvailability
        fields = '__all__'

class BusinessAccountSerializer(serializers.ModelSerializer):
    business_availability = BusinessAvailabilitySerializer()
    address = CurrentCityAddressSerializer()
    business_category = BusinessCategorySerializer()  # Include the BusinessCategorySerializer

    class Meta:
        model = BusinessAccount
        fields = '__all__'

    def create(self, validated_data):
        business_availability_data = validated_data.pop('business_availability')
        address_data = validated_data.pop('address')
        business_category_data = validated_data.pop('business_category')  # Extract business category data

        business_availability = BusinessAvailability.objects.create(**business_availability_data)
        address = Address.objects.create(**address_data)
        business_category = BusinessCategory.objects.create(**business_category_data)  # Create business category

        business_profile = BusinessAccount.objects.create(
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
        ret['address'] = CurrentCityAddressSerializer(instance.address).data
        ret['business_category'] = BusinessCategorySerializer(instance.business_category).data
        return ret



class UserProfileSerializer(serializers.ModelSerializer):
    stickers = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    sticking = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    user = UserSerializer(required=False)


    class Meta:
        model = UserProfile
        fields = ('user','work', 'date_of_birth', 'gender', 'custom_gender',  'stickers', 'sticking')

        

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'password', 'profile')

    extra_kwargs = {
        'password': {'write_only': True},  # Password field should be write-only
    }

    def update(self, instance, validated_data):
        # Update User fields
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.username = validated_data.get('username', instance.username)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        
        # Update UserProfile fields
        profile_data = validated_data.get('profile', {})
        profile = instance.profile

        profile.work = profile_data.get('work', profile.work)
        profile.date_of_birth = profile_data.get('date_of_birth', profile.date_of_birth)
        profile.gender = profile_data.get('gender', profile.gender)
        profile.custom_gender = profile_data.get('custom_gender', profile.custom_gender)

        # Update Address fields (including current city)
        address_data = profile_data.get('address', {})
        address = profile.address

        address.current_city = address_data.get('current_city', address.current_city)

        # Save both User, UserProfile, and Address instances
        instance.save()
        profile.save()
        address.save()

        return instance


class UserListSerializer(serializers.ModelSerializer):
    sticking_count = serializers.SerializerMethodField()
    sticker_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'sticking_count', 'sticker_count')

    def get_sticking_count(self, obj):
        try:
            user_profile = UserProfile.objects.get(user=obj)
            return user_profile.sticking.count()
        except UserProfile.DoesNotExist:
            return 0

    def get_sticker_count(self, obj):
        try:
            user_profile = UserProfile.objects.get(user=obj)
            return user_profile.stickers.count()
        except UserProfile.DoesNotExist:
            return 0


class UserDeletionSerializer(serializers.Serializer):
    reason_choice = serializers.CharField(write_only = True, required = False)
    reason = serializers.CharField(write_only = True, required = False)
    password = serializers.CharField(write_only=True, required=True)


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class VerificationSerializer(serializers.ModelSerializer):

    class Meta:
        models = Verification
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class BlockedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockedUser
        fields = ('blocker', 'blocked_user', 'reason')
    

class BusinessAccountRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessAccount
        fields = ['business_name', 'business_password', 'role', 'image', 'business_category', 'year_founded']

class BusinessAccountLoginSerializer(serializers.Serializer):
    business_name = serializers.CharField()
    business_password = serializers.CharField()



class GeneralSearchSerializer(serializers.Serializer):
    query = serializers.CharField()

class FlagUserProfileSerializer(serializers.Serializer):
    username = serializers.CharField()



class BusinessAccountChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not check_password(value, user.businessaccount.business_password):
            raise serializers.ValidationError("Incorrect old password.")
        return value


class CheckProfileUpdateStatus(serializers.Serializer):
    class Meta:
        model = UserProfile
        fields = ('has_updated_profile',)



class UserSerializer2(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class ProfileMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileMedia
        fields = '__all__'

class UserProfileSerializer2(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    date_of_birth = serializers.DateField(format='%Y-%m-%d')
    # user = UserSerializer2()
    # profile_image = ProfileMediaSerializer()

    class Meta:
        model = UserProfile
        fields = ['user', 'work', 'date_of_birth', 'gender', 'custom_gender', 'religion']




class Acct_Sync_Serializer(serializers.ModelSerializer):

    class Meta:
        model = User

    def validate(self, attrs):
        return super().validate(attrs)
    
    

    