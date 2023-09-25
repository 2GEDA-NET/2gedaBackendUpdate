# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'genres', GenreViewSet)
router.register(r'userprofiles', UserProfileViewSet)
router.register(r'playlists', PlaylistViewSet)
router.register(r'songs', SongViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    # Add other URL patterns here as needed.
    path('stereo/register/', StereoAccountRegistrationView.as_view(), name='stereo_account_register'),
    path('stereo/login/', StereoAccountLoginView.as_view(), name='stereo_account_login'),

]
