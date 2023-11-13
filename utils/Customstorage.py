from django.core.files.storage import get_storage_class
from storages.backends.s3boto3 import S3Boto3Storage
from tempfile import SpooledTemporaryFile
from PIL import Image, ImageEnhance
from io import BytesIO
from django.conf import settings
import base64
import os
import io
from django.http import HttpResponse

#videos
from django.conf import settings
from moviepy.editor import *
from tempfile import NamedTemporaryFile
from moviepy.config import change_settings

temp_path = settings.MEDIA_ROOT

temp_path = temp_path + '/' + 'temp'

change_settings({"IMAGEMAGICK_BINARY": temp_path})


class CustomS3Boto3Storage(S3Boto3Storage):

    def download_file(self, file_key, watermark_path):
        """
        Download a file from the specified S3 bucket using the file_key.
        """
        file_content = self.open(file_key).read()

       
        original_image = Image.open(BytesIO(file_content))


        watermark = Image.open(watermark_path)

        watermark = watermark.resize((60,60), Image.Resampling.LANCZOS)

        original_image.paste(watermark, (150, 150), mask=watermark)

        output = BytesIO()
        original_image.save(output, format='JPEG')  
        output.seek(0)

        # Create a response with the watermarked image content
        response = HttpResponse(output.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{file_key}"'



        return response
    


class CustomS3BotoVideoStorage(S3Boto3Storage):

    def download_file(self, file_key):
        # Read the video file content from S3
        video_content = self.open(file_key).read()

        with NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            temp_file.write(video_content)
            temp_file_path = temp_file.name
        try:
            # Create a VideoFileClip from the content
            video = VideoFileClip(temp_file_path, audio=True)
            w, h = video.size

            # Create a TextClip for the watermark
            txt = TextClip("2geda", font='Amiri-regular', color='white', fontsize=24)

            # Create a colored background for the text
            txt_col = txt.on_color(size=(video.w + txt.w, txt.h-10),
                                color=(0, 0, 0), pos=(6, 'center'), col_opacity=0.6)

            # Set the position of the text clip
            txt_mov = txt_col.set_pos(lambda t: (max(w/30, int(w-0.5*w*t)), max(5*h/6, int(100*t))))

            # Composite the video and text clips
            final = CompositeVideoClip([video, txt_mov])
            final.duration = video.duration

            # Save the watermarked video to BytesIO
            output = BytesIO()
            final.write_videofile(output, fps=24, codec='libx264')

            # Seek to the beginning of the BytesIO buffer
            output.seek(0)

            # Create a Django HttpResponse with the watermarked video content
            response = HttpResponse(output.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{file_key}"'

            return response
        finally:
            os.remove(temp_file_path)


    # def download_file(self, file_key, watermark_path):
    #     file_content = self.open(file_key).read()
    #     file_content = self.open(file_key).read()
    #     video =  VideoFileClip(file_content, audio=True)
    #     w,h = video.size 

    #     txt = TextClip("THE WATERMARK TEXT", font='Amiri-regular',
	#                color='white',fontsize=24)

    #     txt_col = txt.on_color(size=(video.w + txt.w,txt.h-10),
    #                     color=(0,0,0), pos=(6,'center'), col_opacity=0.6)
        
    #     txt_mov = txt_col.set_pos( lambda t: (max(w/30,int(w-0.5*w*t)),
    #                               max(5*h/6,int(100*t))) )
        
    #     final = CompositeVideoClip([video,txt_mov])
    #     final.duration = video.duration

    #     output = BytesIO()
    #     final.write_videofile(output,fps=24,codec='libx264')
    #     # original_image.save(output, format='JPEG')  
    #     output.seek(0)


    #     response = HttpResponse(output.read(), content_type='application/octet-stream')
    #     response['Content-Disposition'] = f'attachment; filename="{file_key}"'


    




       