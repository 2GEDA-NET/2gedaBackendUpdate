# Create a file called custom_auth_backends.py in your app directory

from django.contrib.auth.backends import ModelBackend
from .models import BusinessAccount, User
from django.db.models import Q

class BusinessAccountAuthBackend(ModelBackend):
    def businessauthenticate(self, request, username=None, password=None, **kwargs):
        try:
            business_account = BusinessAccount.objects.get(
                business_name=username,
                business_password=password
            )
            return business_account.profile.user  # Return the associated user
        except BusinessAccount.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return BusinessAccount.objects.get(profile__user__id=user_id).profile.user
        except BusinessAccount.DoesNotExist:
            return None

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Try to authenticate by username
        user = User.objects.filter(username=username).first()
        if not user:
            # Try to authenticate by email
            user = User.objects.filter(email=username).first()
        if not user:
            # Try to authenticate by phone number
            user = User.objects.filter(phone_number=username).first()

        if user and user.check_password(password):
            return user
        return None