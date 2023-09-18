from django.urls import path
from .views import *

urlpatterns = [
    path('options/', OptionListCreateView.as_view(), name='option-list-create'),
    path('options/<int:pk>/', OptionDetailView.as_view(), name='option-detail'),

    path('votes/', VoteListCreateView.as_view(), name='vote-list-create'),
    path('votes/<int:pk>/', VoteDetailView.as_view(), name='vote-detail'),

    path('polls/', PollListCreateView.as_view(), name='poll-list-create'),
    path('polls/<int:pk>/', PollDetailView.as_view(), name='poll-detail'),
]
