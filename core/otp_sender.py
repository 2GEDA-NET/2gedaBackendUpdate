from django.core.mail import send_mail, BadHeaderError

from django.conf import settings

from .models import OtpReceiver, UserModel

from rest_framework import status

from rest_framework.response import Response
import random

from TogedaBackend import settings

from twilio.rest import Client

from django.core.exceptions import ValidationError

from sendgrid import SendGridAPIClient

from sendgrid.helpers.mail import Mail
import hashlib




def registration_send_otp(user_input, is_email=True):
    try:
        subject = 'Your account verification OTP'
        otp_value = str(random.randint(10000, 99999))
        message = f'Your 2geda registration OTP is {otp_value}'
        print(message)

        if is_email:
            message = Mail(
                from_email=settings.EMAIL_BACKEND,
                to_emails=user_input,
                subject='2GEDA Registration OTP',
                html_content=f'Your 2GEDA registration OTP is <br/><strong><h3>{otp_value}</h3></strong>'
            )
            sender = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sender.send(message)
            # print(response.body)
        else:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=user_input
            )

    
        sha256 = hashlib.sha256()
        sha256.update(otp_value.encode('utf-8'))
        otp_value = sha256.hexdigest()
        # Check whether user_input is an email or a phone number
        if is_email:
            user = UserModel.objects.get(email=user_input)
        else:
            user = UserModel.objects.get(phone=user_input)

        # Create or update an OTP record in the OtpReceiver model
        otp_receiver, created = OtpReceiver.objects.get_or_create(user=user, defaults={'otp': otp_value})

        # If not created, update the OTP value
        if not created:
            otp_receiver.otp = otp_value
            otp_receiver.save()

        return otp_receiver

    except BadHeaderError as e:
        # Handle the BadHeaderError by logging the error
        # print(f"BadHeaderError: {str(e)}")
        return None


def password_send_otp(user_input, is_email=True):

    try:

        subject = 'Your account verification OTP'

        otp_value = str(random.randint(10000, 99999))

        mesage = f'Your 2GEDA password OTP is {otp_value}'
        print(mesage)
        

        if is_email:

            message = Mail(from_email=settings.EMAIL_BACKEND,

            to_emails=user_input,

            subject='2GEDA Registration OTP',

            html_content=f'Your 2GEDA forget password reset OTP is <br/><strong><h3>{otp_value}</h3></strong>')

            sender = SendGridAPIClient(settings.SENDGRID_API_KEY)
            sender.send(message)   

        else:
            

            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

            message = client.messages.create(

                body=mesage,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=user_input

            )

        # Check whether user_input is an email or a phone number
        sha256 = hashlib.sha256()
        sha256.update(otp_value.encode('utf-8'))
        otp_value = sha256.hexdigest()
        if is_email:

            user = UserModel.objects.get(email=user_input)

        else:

            user = UserModel.objects.get(phone=user_input)


        # Create or update an OTP record in the OtpReceiver model

        otp_receiver, created = OtpReceiver.objects.get_or_create(user=user, defaults={'otp': otp_value})


        # If not created, update the OTP value

        if not created:

            otp_receiver.otp = otp_value

            otp_receiver.save()
            

        return otp_receiver

    except BadHeaderError:

        return Response(status=status.HTTP_406_NOT_ACCEPTABLE)


