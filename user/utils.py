from user.models import Notification


def send_notification(recipient, sender, message):
    notification = Notification(recipient=recipient, sender=sender, message=message)
    notification.save()
