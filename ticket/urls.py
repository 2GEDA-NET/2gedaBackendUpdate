from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'event_categories', views.EventCategoryViewSet)
router.register(r'events', views.EventViewSet)
router.register(r'tickets', views.TicketViewSet)
router.register(r'banks', views.BankViewSet)
router.register(r'payout_infos', views.PayOutInfoViewSet)
router.register(r'withdraws', views.WithdrawViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
