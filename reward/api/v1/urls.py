from django.urls import path
from .views import (
    Reward_User,
    Get_Rewards,
    Get_All_Rewards,
    Claim_Reward,
    Claims_Record
)

urlpatterns = [
    path('user/', Reward_User.as_view()),
    path('get', Get_Rewards.as_view()),
    path("get-all/", Get_All_Rewards.as_view()),
    path("claim/", Claim_Reward.as_view()),
    path("claim/history/", Claims_Record.as_view()),
]
