from django.shortcuts import render
from rest_framework import generics
from .models import *
from rest_framework.authentication import *
from .serializers import *
from rest_framework.permissions import *
from .permissions import *
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework import status, permissions
from rest_framework.response import Response
import requests


# Create your views here.
def product_list(request):
    if request.method == 'GET':
        # products = Product.objects.all().order_by('create_at').reverse()
        products = Product.objects.prefetch_related('product_imgs').order_by('create_at').reverse()
        serializer = ProductSerializer(products, many=True)
        return JsonResponse(serializer.data, safe=False)
    
    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = ProductSerializer(data=data)
        
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status = 201)
        return JsonResponse(serializer.errors, status = 400)


# Advert
class AdvertList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Advert.objects.all()
    serializer_class = AdvertSerializer

class AdvertDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Advert.objects.all()
    serializer_class = AdvertSerializer

# Product Category Views
class ProductCategoryList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer

class ProductCategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer

# Store Views
class StoreList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Store.objects.all()
    serializer_class = StoreSerializer

class StoreDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Store.objects.all()
    serializer_class = StoreSerializer

# Product Views
class ProductList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

# ProductReview
class ProductReviewListCreateView(generics.ListCreateAPIView):
    queryset = ProductReview.objects.all()
    authentication_classes = (TokenAuthentication,)
    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # You can customize permissions here

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ProductReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (TokenAuthentication,)
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]  # Custom permission for owner

# CartItem Views
class CartItemList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

class CartItemDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

# Order Views
class OrderList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class OrderDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class SaleHistoryView(APIView):
    def get(self, request, *args, **kwargs):
        # Get the currently authenticated business
        business = request.user.businessprofile  # Assuming you have a user profile model linked to the business

        # Retrieve sale history for the business
        sale_history = SaleHistory.objects.filter(product__business=business).order_by('sale_date')
        serializer = SaleHistorySerializer(sale_history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MarkProductSoldView(APIView):
    def post(self, request):
        serializer = MarkProductSoldSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data.get('product_id')
            try:
                product = Product.objects.get(id=product_id, business__user=request.user)
                product.is_sold = True
                product.save()
                return Response({'message': 'Product marked as sold.'}, status=status.HTTP_200_OK)
            except Product.DoesNotExist:
                return Response({'error': 'Product not found or you do not have permission to mark it as sold.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PromoteProductView(APIView):
    def post(self, request):
        serializer = PromotionSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data.get('product_id')
            promotion_plan_id = serializer.validated_data.get('promotion_plan_id')
            try:
                product = Product.objects.get(id=product_id, business__user=request.user)
                promotion_plan = PromotionPlan.objects.get(id=promotion_plan_id)
                amount_kobo = int(promotion_plan.amount * 100)  # Convert amount to kobo (Paystack uses kobo)
                email = request.user.email
                callback_url = settings.PAYSTACK_CALLBACK_URL

                # Create a payment request to Paystack
                paystack_url = "https://api.paystack.co/transaction/initialize"
                paystack_data = {
                    "email": email,
                    "amount": amount_kobo,
                    "callback_url": callback_url,
                    "metadata": {
                        "product_id": product_id,
                        "promotion_plan_id": promotion_plan_id
                    }
                }
                headers = {
                    "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
                    "Content-Type": "application/json"
                }

                # Make the API request to Paystack
                response = requests.post(paystack_url, json=paystack_data, headers=headers)

                # Extract the payment URL from the Paystack response
                data = response.json()
                payment_url = data.get("data", {}).get("authorization_url")

                return Response({'payment_url': payment_url}, status=status.HTTP_200_OK)
            except (Product.DoesNotExist, PromotionPlan.DoesNotExist):
                return Response({'error': 'Product or promotion plan not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaystackCallbackView(APIView):
    def post(self, request):
        reference = request.data.get('reference')

        # Verify the payment status with Paystack
        verify_url = f"https://api.paystack.co/transaction/verify/{reference}"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        response = requests.get(verify_url, headers=headers)

        # Handle the Paystack response
        data = response.json()
        status_code = data.get('status')
        if status_code == 200:
            # Payment was successful
            metadata = data.get('data', {}).get('metadata', {})
            product_id = metadata.get('product_id')
            promotion_plan_id = metadata.get('promotion_plan_id')

            # Update the product and mark it as promoted
            try:
                product = Product.objects.get(id=product_id)
                promotion_plan = PromotionPlan.objects.get(id=promotion_plan_id)
                product.is_promoted = True
                product.promotion_plan = promotion_plan
                product.save()
                return Response({'message': 'Product promoted successfully.'}, status=status.HTTP_200_OK)
            except (Product.DoesNotExist, PromotionPlan.DoesNotExist):
                return Response({'error': 'Product or promotion plan not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Payment failed
            return Response({'error': 'Payment verification failed.'}, status=status.HTTP_400_BAD_REQUEST)
