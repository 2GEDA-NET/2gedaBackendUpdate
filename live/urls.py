from django.urls import path
from .views import *


urlpatterns = [
    path('video-sessions/', VideoSessionListCreateView.as_view(), name='video-session-list-create'),
    path('video-sessions/<int:pk>/', VideoSessionDetailView.as_view(), name='video-session-detail'),
    path('video-sessions/<int:pk>/update/', VideoSessionUpdateView.as_view(), name='video-session-update'),
    path('videos/', VideoUploadView.as_view(), name='video-upload'),
    path('videos/list/', VideoListView.as_view(), name='video-list'),
    # Add more URL patterns for delete, or any other views you need
]
