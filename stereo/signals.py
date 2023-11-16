from pydub import AudioSegment
from pydub.playback import play
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Song
from datetime import timedelta

@receiver(post_save, sender=Song)
def set_song_duration(sender, instance, **kwargs):
    try:
        # Open the audio file using Django storage's open method
        with instance.audio_file.open('rb') as audio_file:
            # Load audio using pydub's AudioSegment.from_file method
            audio = AudioSegment.from_file(audio_file)

            # Play the audio (this is optional and can be removed if not needed)
            play(audio)

            # Calculate duration
            duration_seconds = audio.duration_seconds
            instance.duration = timedelta(seconds=duration_seconds)
    except Exception as e:
        # Log the exception or handle it accordingly
        raise ValidationError(f"Error calculating audio duration: {e}")
