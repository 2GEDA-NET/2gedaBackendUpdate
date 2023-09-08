from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from .views import *

app_name = 'users'

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'user-profiles', UserProfileViewSet)
router.register(r'business-categories', BusinessCategoryViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('register/', create_user, name='user_register'),
    path('login/', Login.as_view(), name='login'),
    path('', UserAPIView.as_view(), name='user_detail'),
    path('get-csrf-token/', get_csrf_token, name='get-csrf-token'),
    path('api-auth-token', obtain_auth_token, name='api_token'),
    path('report_user/', report_user, name='report_user'),
    # path('reported_user_list/', ReportUserViewSet.as_view(), name='reported_user_list'),
    path('create-business-profile/', create_business_profile,
         name='create-business-profile'),
    path('update-business-profile/<int:pk>/',
         update_business_profile, name='update-business-profile'),
    path('business-availability/', BusinessAvailabilityListCreateView.as_view(),
         name='business-availability-list'),
    path('business-availability/<int:pk>/',
         BusinessAvailabilityDetailView.as_view(), name='business-availability-detail'),

    path('business-profile/', BusinessProfileListCreateView.as_view(),
         name='business-profile-list'),
    path('business-profile/<int:pk>/', BusinessProfileDetailView.as_view(),
         name='business-profile-detail'),

    path('business-category/', BusinessCategoryListCreateView.as_view(),
         name='business-category-list'),
    path('business-category/<int:pk>/',
         BusinessCategoryDetailView.as_view(), name='business-category-detail'),

    path('address/', AddressListCreateView.as_view(), name='address-list'),
    path('address/<int:pk>/', AddressDetailView.as_view(), name='address-detail'),


]

urlpatterns += router.urls
