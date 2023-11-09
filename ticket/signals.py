from django.db.models.signals import post_save
from django.dispatch import receiver
from user.models import Notification
from .models import Event


@receiver(post_save, sender=Event)
def event_created_notification(sender, instance, created, **kwargs):
    if created:
        event_owner = instance.user  # The user who created the event
        message = f"Event '{instance.title}' was successfully created."

        # Send a notification to the event owner
        event_owner_notification = Notification(
            recipient=event_owner,
            sender=event_owner,
            message=message,
        )
        event_owner_notification.save()

        # Iterate through followers and send invitations
        for sticker in event_owner.userprofile.stickers.all():
            invitation_message = f"{event_owner.username} has created an event: '{instance.title}'. Would you like to join?"

            # Send an invitation notification to followers
            sticker_invitation_notification = Notification(
                recipient=sticker,
                sender=event_owner,
                message=invitation_message,
            )
            sticker_invitation_notification.save()