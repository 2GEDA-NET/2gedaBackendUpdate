from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Video

@receiver(post_save, sender=Video)
def convert_video_to_hls(sender, instance, created, **kwargs):
    if created and not instance.hls_ready:
        # Only trigger conversion for newly created videos that haven't been processed
        from subprocess import Popen, PIPE
        import os

        input_path = os.path.join(settings.MEDIA_ROOT, str(instance.video_file))
        output_path = os.path.join(settings.MEDIA_ROOT, 'hls', str(instance.id))

        # Create the output directory for HLS segments
        os.makedirs(output_path, exist_ok=True)

        # Run FFmpeg to convert the video to HLS
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-c:v', 'h264',
            '-hls_time', '10',  # Segment duration in seconds
            '-hls_list_size', '0',  # Keep all segments in the playlist
            '-start_number', '0',
            '-f', 'hls',
            os.path.join(output_path, 'index.m3u8')
        ]

        process = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            # Video conversion successful
            instance.hls_ready = True
            instance.save()
        else:
            # Video conversion failed
            instance.delete()  # Delete the video record if conversion fails

# Make sure to import 'settings' from your Django project's settings module
from django.conf import settings
