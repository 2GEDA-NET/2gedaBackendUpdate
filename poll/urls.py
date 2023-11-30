from django.urls import path
from .views import *

urlpatterns = [
    path('register/<uuid:pk>/', RegisterVoter.as_view()),
    path('options/', OptionListCreateView.as_view(), name='option-list-create'),
    path('options/<int:pk>/', OptionDetailView.as_view(), name='option-detail'),
    path('votes/', VoteListCreateView.as_view(), name='vote-list-create'),
    path('votes/<int:pk>/', VoteDetailView.as_view(), name='vote-detail'),
    path('polls/', PollListCreateView.as_view(), name='poll-list-create'),
    path('polls/<int:pk>/', PollDetailView.as_view(), name='poll-detail'),
    path('active-polls/', ActivePollsView.as_view(), name='active-polls'),
    path('ended-polls/', EndedPollsView.as_view(), name='ended-polls'),
    path('close-poll/<int:poll_id>/', ClosePollView.as_view(), name='close-poll'),
    path('private-polls/', PrivatePollsView.as_view(), name='private-polls'),
    path('public-polls/', PublicPollsView.as_view(), name='public-polls'),
    path('create-poll/', CreatePollView.as_view(), name='create-poll'),
    path('search-polls/', SearchPollsView.as_view(), name='search-polls'),
    path('suggested-polls/', SuggestedPollsAPIView.as_view(), name='suggested-polls'),
    path('log-poll-view/<int:poll_id>/', log_poll_view, name='log-poll-view'),
    path('access-request/', AccessRequestView.as_view(), name='access-request'),
    path('approve-access/', AccessApprovalView.as_view(), name='approve-access'),
    path('deny-access/', AccessDeclineView.as_view(), name='deny-access'),
    path('initiate-payment/', initiate_payment, name='initiate-payment'),
    path('paystack-callback/', paystack_callback, name='paystack-callback'),
    path('cast-vote/', cast_votes, name='cast-vote'),
    path('polls-with-vote-count/', PollsWithVoteCountView.as_view(), name='polls-with-vote-count'),
    path('polls/results/<int:poll_id>/', PollResultsView.as_view(), name='poll-results'),
    path('payment/', PollsPaymentView.as_view()),


]
