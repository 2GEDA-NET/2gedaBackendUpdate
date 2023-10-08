from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserModel, UserProfile
from rest_framework.authtoken.models import Token

# @receiver(post_save, sender=UserProfile)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         print("User profile created for:", instance.username)
#         UserProfile.objects.create(user=instance)

# @receiver(post_save, sender=UserModel)
# def save_user_profile(sender, instance, **kwargs):
#     print("User profile saved for:", instance.username)
#     instance.userprofile.save()

# @receiver(post_save, sender=UserModel)
# def create_auth_token(sender, instance=None, created=False, **kwargs):
#     if created:
#         Token.objects.create(user=instance)



@receiver(post_save, sender=UserProfile)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        print("User profile created for:", instance.user.username)
        UserProfile.objects.create(user=instance.user)

# Keep either create_auth_token or save_user_profile based on your needs.
@receiver(post_save, sender=UserModel)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
