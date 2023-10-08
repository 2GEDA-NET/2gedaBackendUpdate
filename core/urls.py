from django.urls import path, include
from . views import *
from rest_framework.routers import DefaultRouter
from django.conf.urls.static import static

router = DefaultRouter()

router.register('register', RegisterView, basename='signup')
router.register('user-profiles', UserProfileViewSet)
router.register(r'business-categories', BusinessCategoryViewSet)
router.register(r'password-change', PasswordChangeViewSet,
                basename='password-change')


# router.register('verify-otp', VerifyOtpView, basename='verify_otp')



# urlpatterns = router.urls

urlpatterns = [
    path('', include(router.urls)),
    path('register/resend-otp/', RegisterView.as_view({'post': 'resend_otp'}), name='resend-otp'),
    # path('register/resend-otp/', ResendOTPView.as_view(), name ='resend-otp'),
    path('registration/verify-otp/', VerifyOtpView.as_view(), name='verify_otp'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password/reset-page/', PasswordResetRequestView.as_view({'post': 'create'}), name='password_reset'),
    path('resend/password-otp/', PasswordResetRequestView.as_view({'post': 'password_resend_otp'}), name='password-reset-resend-otp'),
    path('confirm/password-page/', PasswordResetConfirmView.as_view(), name='password_confirm'),
    path('update-profile/', update_user_profile, name='update_user_profile'),
    path('search-user/', UserSearchAPIView.as_view(), name='search_user'),
    path('delete-account/', delete_account, name='delete_account'),
    path('delete-user/<str:username>/', delete_account_by_username,
         name='delete_account_by_username'),
    # path('delete-user-by-id/<int:user_id>/',
    #      delete_account_by_id, name='delete_account_by_id'),
    path('delete-user-by-username-or-id/', delete_user_by_username_or_id,
         name='delete_user_by_username_or_id'),
    path('block/', block_user, name='block-user'),
    path('blocked-users/', list_blocked_users, name='list-blocked-users'),


    #     Stick urls
    path('stick/<int:user_id>/', stick_user, name='stick_user'),
    path('list-stickers/<int:user_id>/',
         list_stickers, name='list_stickers'),
    path('list-sticking/<int:user_id>/',
         list_sticking, name='list_sticking'),
    path('my-sticking/', my_sticking, name='my_sticking'),
    path('my-stickers/', my_stickers, name='my_stickers'),


    # CRSF token
    # path('get-csrf-token/', get_csrf_token, name='get-csrf-token'),

    #     Report Users urls
    path('report_user/', report_user, name='report_user'),
    path('reported_user_list/<int:user_id>/',
         ReportUserViewSet.as_view(), name='reported_user_list'),

    #     Business Profile urls
    path('create-business-profile/', create_business_profile,
         name='create-business-profile'),
    path('update-business-profile/<int:pk>/',
         update_business_profile, name='update-business-profile'),
    path('business-availability/', BusinessAvailabilityListCreateView.as_view(),
         name='business-availability-list'),
    path('business-availability/<int:pk>/',
         BusinessAvailabilityDetailView.as_view(), name='business-availability-detail'),

    path('business-profile/', BusinessAccountListCreateView.as_view(),
         name='business-profile-list'),
    path('business-profile/<int:pk>/', BusinessAccountDetailView.as_view(),
         name='business-profile-detail'),

    path('business-category/', BusinessCategoryListCreateView.as_view(),
         name='business-category-list'),
    path('business-category/<int:pk>/',
         BusinessCategoryDetailView.as_view(), name='business-category-detail'),


    # Address Urls
    path('address/', AddressListCreateView.as_view(), name='address-list'),
    path('address/<int:pk>/', AddressDetailView.as_view(), name='address-detail'),

    # Verification Urls
    path('create-verification/', VerificationCreateView.as_view(),
         name='verification-create'),
    path('verification/<int:pk>/', VerificationRetrieveView.as_view(),
         name='verification-detail'),

    # Notification url
    path('get-notifications/', get_notifications, name='get-notification'),

    # Get conversations encryption keys
    path('get_encryption_keys/', EncryptionKeyAPIView.as_view(),
         name='get_encryption_keys'),
    # Business authentication

    path('business/register/', BusinessAccountRegistrationView.as_view(),
         name='business_account_register'),
    path('business/login/', BusinessAccountLoginView.as_view(),
         name='business_account_login'),
    path('business-accounts/', ManagedBusinessAccountsView.as_view(),
         name='managed_business_accounts'),
    path('business/change-password/',
         BusinessAccountChangePasswordView.as_view(), name='business_change_password'),


    path('flag-profile/', flag_user_profile, name='flag-user-profile'),

]

urlpatterns += router.urls

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)








# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from rest_framework.authtoken.views import obtain_auth_token
# from django.conf import settings
# from django.conf.urls.static import static
# from .views import *

# app_name = 'users'

# router = DefaultRouter()
# router.register(r'users', UserViewSet, basename='user')
# router.register(r'user-profiles', UserProfileViewSet)
# router.register(r'business-categories', BusinessCategoryViewSet)
# router.register(r'password-change', PasswordChangeViewSet,
#                 basename='password-change')

# urlpatterns = [
#     path('api/', include(router.urls)),

#     #     Authentication urls
#     path('register/', create_user, name='user_register'),
#     path('login/', obtain_auth_token, name='api_token'),
#     #     path('password-change/', PasswordChangeViewSet.as_view, name='change_password'),
#     path('', UserAPIView.as_view(), name='user_detail'),
#     path('update-profile/', update_user_profile, name='update_user_profile'),
#     path('search-user/', UserSearchAPIView.as_view(), name='search_user'),
#     path('delete-account/', delete_account, name='delete_account'),
#     path('delete-user/<str:username>/', delete_account_by_username,
#          name='delete_account_by_username'),
#     path('delete-user-by-id/<int:user_id>/',
#          delete_account_by_id, name='delete_account_by_id'),
#     path('delete-user-by-username-or-id/', delete_user_by_username_or_id,
#          name='delete_user_by_username_or_id'),
#     path('block/', block_user, name='block-user'),
#     path('blocked-users/', list_blocked_users, name='list-blocked-users'),


#     #     Stick urls
#     path('stick/<int:user_id>/', stick_user, name='stick_user'),
#     path('list-stickers/<int:user_id>/',
#          list_stickers, name='list_stickers'),
#     path('list-sticking/<int:user_id>/',
#          list_sticking, name='list_sticking'),
#     path('my-sticking/', my_sticking, name='my_sticking'),
#     path('my-stickers/', my_stickers, name='my_stickers'),


#     # CRSF token
#     path('get-csrf-token/', get_csrf_token, name='get-csrf-token'),

#     #     Report Users urls
#     path('report_user/', report_user, name='report_user'),
#     path('reported_user_list/<int:user_id>/',
#          ReportUserViewSet.as_view(), name='reported_user_list'),

#     #     Business Profile urls
#     path('create-business-profile/', create_business_profile,
#          name='create-business-profile'),
#     path('update-business-profile/<int:pk>/',
#          update_business_profile, name='update-business-profile'),
#     path('business-availability/', BusinessAvailabilityListCreateView.as_view(),
#          name='business-availability-list'),
#     path('business-availability/<int:pk>/',
#          BusinessAvailabilityDetailView.as_view(), name='business-availability-detail'),

#     path('business-profile/', BusinessAccountListCreateView.as_view(),
#          name='business-profile-list'),
#     path('business-profile/<int:pk>/', BusinessAccountDetailView.as_view(),
#          name='business-profile-detail'),

#     path('business-category/', BusinessCategoryListCreateView.as_view(),
#          name='business-category-list'),
#     path('business-category/<int:pk>/',
#          BusinessCategoryDetailView.as_view(), name='business-category-detail'),


#     # Address Urls
#     path('address/', AddressListCreateView.as_view(), name='address-list'),
#     path('address/<int:pk>/', AddressDetailView.as_view(), name='address-detail'),

#     # Verification Urls
#     path('create-verification/', VerificationCreateView.as_view(),
#          name='verification-create'),
#     path('verification/<int:pk>/', VerificationRetrieveView.as_view(),
#          name='verification-detail'),

#     # Notification url
#     path('get-notifications/', get_notifications, name='get-notification'),

#     # Get conversations encryption keys
#     path('get_encryption_keys/', EncryptionKeyAPIView.as_view(),
#          name='get_encryption_keys'),
#     # Business authentication

#     path('business/register/', BusinessAccountRegistrationView.as_view(),
#          name='business_account_register'),
#     path('business/login/', BusinessAccountLoginView.as_view(),
#          name='business_account_login'),
#     path('business-accounts/', ManagedBusinessAccountsView.as_view(),
#          name='managed_business_accounts'),
#     path('business/change-password/',
#          BusinessAccountChangePasswordView.as_view(), name='business_change_password'),


#     path('flag-profile/', flag_user_profile, name='flag-user-profile'),

# ]

# urlpatterns += router.urls

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL,
#                           document_root=settings.MEDIA_ROOT)

