from core.models import Notification


def send_post_promotion_notification(user, message):
    # Create a notification for the user
    Notification.objects.create(
        recipient=user,
        verb='promoted_post',  # You can customize this verb based on your app's notification system
        description=message,
    )
