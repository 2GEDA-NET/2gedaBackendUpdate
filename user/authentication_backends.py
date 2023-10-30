# Create a file called custom_auth_backends.py in your app directory

from django.contrib.auth.backends import ModelBackend
from .models import BusinessAccount, User

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
        try:
            # Check if username is an email or phone number
            if '@' in username:
                user = User.objects.get(email=username)
            elif username.isdigit():
                user = User.objects.get(phone_number=username)
            else:
                user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
