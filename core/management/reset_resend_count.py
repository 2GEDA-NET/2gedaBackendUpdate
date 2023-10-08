# from django.core.management.base import BaseCommand
# from background_task.models import Task
# from datetime import timedelta
# from django.utils import timezone
# from core.models import UserModel  # Replace 'yourapp' with your actual app name

# class Command(BaseCommand):
#     help = 'Reset resend_count for users after 24 hours'

#     def handle(self, *args, **kwargs):
#         # Find users whose resend_count should be reset
#         users_to_reset = UserModel.objects.filter(
#             resend_count__gt=0,  # Users with a resend_count greater than 0
#             registration_timestamp__lte=timezone.now() - timedelta(hours=24)  # Users registered more than 24 hours ago
#         )

#         # Reset resend_count for eligible users
#         for user in users_to_reset:
#             user.resend_count = 0
#             user.save()

#         # Log the number of users whose resend_count was reset
#         self.stdout.write(self.style.SUCCESS(f'Reset resend_count for {len(users_to_reset)} users.'))