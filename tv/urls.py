# urls.py
from django.urls import path, include
from .views import *
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'videos', VideoViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'likes', LikeViewSet)
router.register(r'subscriptions', SubscriptionViewSet)
router.register(r'channels', ChannelViewSet)
router.register(r'playlists', PlayListViewSet)
router.register(r'reports', ReportViewSet)
router.register(r'video-tags', VideoTagViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    # Add other URL patterns here as needed.


]
