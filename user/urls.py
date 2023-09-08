from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from .views import *

app_name = 'users'

router = DefaultRouter()
router.register(r'', UserViewSet, basename = 'user')

urlpatterns = [
    path('register/', create_user, name='user_register'),
    path('login/', Login.as_view(), name = 'login'),
    path('', UserAPIView.as_view(), name='user_detail'),
    path('get-csrf-token/', get_csrf_token, name='get-csrf-token'),
    path('api-auth-token', obtain_auth_token, name='api_token'),
    path('report_user/', report_user, name='report_user'),
    # path('reported_user_list/', ReportUserViewSet.as_view(), name='reported_user_list'),
]

urlpatterns += router.urls
