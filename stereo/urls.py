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
]
