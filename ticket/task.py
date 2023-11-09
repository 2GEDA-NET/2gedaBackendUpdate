# tasks.py

from celery import task
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Event
from .utils import send_notification

@task
def send_event_reminders():
    # Define the reminder time frame (e.g., 1 hour before the event)
    reminder_time = timezone.now() + timedelta(hours=1)

    # Query for events starting within the reminder time frame
    upcoming_events = Event.objects.filter(date__gte=reminder_time)

    for event in upcoming_events:
        # Send a reminder to the event organizer
        send_notification(event.user, f"Reminder: Your event '{event.title}' is starting soon!")

        # Send reminders to event attendees (assuming you have a ManyToManyField for attendees)
        for attendee in event.attendees.all():
            send_notification(attendee, f"Reminder: '{event.title}' is starting soon!")
