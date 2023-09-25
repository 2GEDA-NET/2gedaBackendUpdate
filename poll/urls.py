from django.urls import path
from .views import *

urlpatterns = [
    path('options/', OptionListCreateView.as_view(), name='option-list-create'),
    path('options/<int:pk>/', OptionDetailView.as_view(), name='option-detail'),

    path('votes/', VoteListCreateView.as_view(), name='vote-list-create'),
    path('votes/<int:pk>/', VoteDetailView.as_view(), name='vote-detail'),

    path('polls/', PollListCreateView.as_view(), name='poll-list-create'),
    path('polls/<int:pk>/', PollDetailView.as_view(), name='poll-detail'),

    path('active-polls/', ActivePollsView.as_view(), name='active-polls'),
    path('close-poll/<int:poll_id>/', ClosePollView.as_view(), name='close-poll'),
    path('ended-polls/', EndedPollsView.as_view(), name='ended-polls'),
    path('private-polls/', PrivatePollsView.as_view(), name='private-polls'),
    path('public-polls/', PublicPollsView.as_view(), name='public-polls'),
    path('create-poll/', CreatePollView.as_view(), name='create-poll'),
    path('search-polls/', SearchPollsView.as_view(), name='search-polls'),
    path('api/suggested-polls/', SuggestedPollsAPIView.as_view(), name='suggested-polls'),

]
