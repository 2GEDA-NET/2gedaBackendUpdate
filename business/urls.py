from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'addresses', views.AddressViewSet)
router.register(r'phone_numbers', views.PhoneNumberViewSet)
router.register(r'business_directories', views.BusinessDirectoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
