from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for the viewsets
router = DefaultRouter()
router.register(r'event-categories', views.EventCategoryViewSet)
router.register(r'events', views.EventViewSet)
router.register(r'tickets', views.TicketViewSet)
router.register(r'banks', views.BankViewSet)
router.register(r'payout-infos', views.PayOutInfoViewSet)
router.register(r'withdraws', views.WithdrawViewSet)

urlpatterns = [
    path('buy-ticket/', views.buy_ticket, name='buy_ticket'),
    path('request-event-promotion/', views.request_event_promotion, name='request_event_promotion'),
    path('manage-event-promotion-requests/', views.manage_event_promotion_requests, name='manage_event_promotion_requests'),
    path('delete-event/<int:event_id>/', views.delete_event, name='delete_event'),
    path('edit-event/<int:pk>/', views.EditEventAPIView.as_view(), name='edit_event'),
    path('event/<int:event_id>/ticket-report/', views.TicketReportAPIView.as_view(), name='event_ticket_report'),
    path('event/<int:event_id>/download-ticket-report/', views.download_ticket_report, name='download_ticket_report'),
]

# Add the router URLs to the main URL patterns
urlpatterns += router.urls
