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
router.register(r'video-deletions', VideoDeletionViewSet)
router.register(r'video-hidings', VideoHidingViewSet)
router.register(r'video-hidden-list', VideoHiddenListViewSet, basename='videohiddenlist')
router.register(r'video-scheduling', VideoSchedulingViewSet, basename='videoscheduling')



urlpatterns = [
    path('api/', include(router.urls)),
    # Add other URL patterns here as needed.
    path('download/<int:video_id>/', download_movie, name='download_movie'),
    path('register/', TVAccountRegistrationView, name='register_tv_account'),
    path('login/', TVAccountLoginView, name='login_tv_account'),



]
