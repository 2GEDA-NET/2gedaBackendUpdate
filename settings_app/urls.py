from django.urls import path
from . import views

urlpatterns = [
    path('chat-settings/', views.ChatSettingsCreateView.as_view(), name='chat-settings-list'),
    path('chat-settings/<int:pk>/', views.ChatSettingsUpdateView.as_view(), name='chat-settings-detail'),
]







