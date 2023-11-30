from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from .s3 import get_file_from_s3
from decouple import config
from django.conf import settings
import boto3
from PIL import Image, ImageEnhance
import requests
import io
from .Customstorage import CustomS3Boto3Storage, CustomS3BotoVideoStorage
from rest_framework.decorators import permission_classes, api_view
from rest_framework import generics
from .models import Geopraphical_Location
from .serializer import *

# Create your views here.



class Download(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request:Request, format=None):
        
        error={}
        try:
            path = request.data["file"]  
            path = request.data["folder"]  
            
            
        except:
            error['error'] = "requires key 'file' and 'folder' "
            return Response(error, status=400)

        response = None
        s3 = boto3.client(
            's3',
            aws_access_key_id=config("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=config("AWS_SECRET_ACCESS_KEY"),
            region_name=config("AWS_S3_REGION_NAME")
        )
        file = request.data["file"]
        folder = request.data["folder"]
        key = 'download.jpeg'
        try:
            response = s3.generate_presigned_url(
                ClientMethod='get_object',
                Params={'Bucket': config("AWS_STORAGE_BUCKET_NAME"), 'Key': f'{folder}/{file}'},
                ExpiresIn=3600  
            )
            response = requests.get(response)
            
            input_image_bytes = response.content
            print(input_image_bytes)

            output_image_path = settings.MEDIA_ROOT + '/' + ''
            watermark_path = settings.MEDIA_ROOT + '/' + 'watermark.png'
            watermark_image_path = settings.MEDIA_ROOT + '/' + 'watermark.png'
           

            # watermark_data = watermark_data.rstrip("\n").decode("utf-16")
            # watermark_data = watermark_data.split("\r\n")
            watermark = Image.open( watermark_image_path).convert("RGBA")


            # Open the input image from BytesIO
            input_image = Image.open(io.BytesIO(input_image_bytes)).convert("RGBA")

            # Resize watermark to fit on the input image
            width, height = input_image.size
            watermark = watermark.resize((width, height))

            # Create a transparent layer for the watermark
            watermark_with_transparency = Image.new("RGBA", (width, height), (0, 0, 0, 0))

            # Paste the watermark onto the transparent layer
            position = (10, 10)

            watermark_with_transparency.paste(watermark, position, watermark)

            # Blend the input image and the transparent watermark
            output_image = Image.alpha_composite(input_image, watermark_with_transparency)

            # Save the output image
            output_image.save(watermark_image_path, "PNG")


            return Response({'url': response}, status=200)
        
        except Exception as e:
            error["error"] = "could not download  requested file"
            print(e)
            return Response(error, status=400)
            


# class Add_Watermark(APIView):
    
#     def post(self, request, format=None):
#         your_file = request.data["file"]
#         storage = CustomS3Boto3Storage()
#         watermark_path = settings.MEDIA_ROOT + '/' + 'watermark.png'
#         response = storage.download_file( file_key=your_file, watermark_path=watermark_path)

#         return response


@api_view(['GET'])
@permission_classes([AllowAny])
def Add_Watermark(request, filepath):
    # Retrieve the user from the request or any other authentication mechanism
    your_file = filepath
    storage = CustomS3Boto3Storage()
    watermark_path = settings.MEDIA_ROOT + '/' + 'watermark.png'
    response = storage.download_file( file_key=your_file, watermark_path=watermark_path)

    # response['Content-Disposition'] = f'attachment; filename="{your_file}"'
    return response

@api_view(['GET'])
@permission_classes([AllowAny])
def Add_Watermark_video(request, filepath):
    # Retrieve the user from the request or any other authentication mechanism
    your_file = filepath
    storage = CustomS3BotoVideoStorage()  
    watermark_path = settings.MEDIA_ROOT + '/' + 'watermark.png'
    response = storage.download_file(file_key=your_file)

    # response['Content-Disposition'] = f'attachment; filename="{your_file}"'
    return response


class GeographyAPIView(generics.ListCreateAPIView):
    permission_classes=[IsAuthenticated]
    queryset= Geopraphical_Location.objects.all()
    serializer_class = GeographySerializer



class UserGeographyView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request, format=None):
        user_geo = Geopraphical_Location.objects.filter(user= request.user).values()

        return Response(list(user_geo), status=200)
