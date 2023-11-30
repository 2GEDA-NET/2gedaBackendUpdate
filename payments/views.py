from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
import requests
from django.conf import settings
import json
from user.models import User as CustomUser
from .models import *
# Create your views here.

PAYSTACK_SK = settings.PAYSTACK_SECRET_KEY
base_url = "https://api.paystack.co/"

class PayOnlineDone(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self, request, format=None):

        ref = request.GET.get("reference")

        path = f'transaction/verify/{ref}'
        headers = {
            "Authorization": f"Bearer {PAYSTACK_SK}",
            "Content-Type": "application/json",
        }
        url = base_url + path
        response = requests.get(url, headers=headers)
        print("cool")
        ab = json.loads(response.text)
        message =  ab["message"]
        if (response.status_code == 200 and ab['status'] == True) and (ab["message"] == "Verification successful" and ab["data"]["status"] == "success"):
            user_email = ab['data']["customer"]['email']
            print(user_email)
            amount = ab['data']['amount']
            user =  CustomUser.objects.get(email=user_email)
            if Wallet_Funding.objects.filter(user=user).exists():
                the_user = Wallet_Funding.objects.get(user=user)
                the_user.amount = amount
                the_user.save()
            
               
            else:
                Wallet_Funding.objects.create(user=user, amount=amount, medium="paystack")
                Wallet_summary.objects.create()
                return Response({"response":"success"}, status=200)

        return Response({"response" : "Permission denied."}, status=400)
    



