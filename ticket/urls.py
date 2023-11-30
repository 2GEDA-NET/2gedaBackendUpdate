from django.urls import path
from django.conf.urls import include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    EventsView,
    EventsDetailView,
    EventsDestroView,
    EventsCategoryView,
    EventsCategoryDetailView,
    PaymentOnlineApi,
    Ticket_List,
    Ticket_Detail_View,
    Paystack_Verification,
    PayOnlineDone,
    WithdrawDetailView,
    GetPaymentView
)

# Create a router for viewsets
router = DefaultRouter()
router.register(r'event-categories', views.EventCategoryViewSet)
router.register(r'events', views.EventViewSet)
router.register(r'tickets', views.TicketViewSet)
router.register(r'banks', views.BankViewSet)
router.register(r'payout-info', views.PayOutInfoViewSet)
router.register(r'withdraw', views.WithdrawViewSet)

urlpatterns = [
    # ... other URL patterns in your project
    
    # Include the router-generated URLs
    path('api/', include(router.urls)),
    
    # Define custom URLs for API views
    path('events/', EventsView.as_view()),
    path('event/<int:pk>/', EventsDetailView.as_view()),
    path('event/delete/<int:pk>/', EventsDestroView.as_view()),

    #Views for EventsCategory
    path('event-category/',EventsCategoryView.as_view()),
    path('event-category/<int:pk>/', EventsCategoryDetailView.as_view()),

    #Tickets
    path('buy-ticket', PaymentOnlineApi.as_view(), name='buy-ticket'),

    
    path('get-ticket', GetPaymentView.as_view(), name='get-ticket'),

    path('create/', PaymentOnlineApi.as_view(), name='buy-ticket'),
    path('List/', Ticket_List.as_view(), name='buy-ticket'),

    path('detail/<int:pk>/', Ticket_Detail_View.as_view()),

    path('hguh-877892/call-back', PayOnlineDone.as_view()),

    path('verify-payments/', Paystack_Verification.as_view()),
    path('request-event-promotion/', views.request_event_promotion, name='request-event-promotion'),
    path('manage-event-promotion-requests/', views.manage_event_promotion_requests, name='manage-event-promotion-requests'),
    path('delete-event/<int:event_id>/', views.delete_event, name='delete-event'),
    path('ticket-report/<int:event_id>/', views.TicketReportAPIView.as_view(), name='ticket-report'),
    path('download-ticket-report/<int:event_id>/', views.download_ticket_report, name='download-ticket-report'),
    path('edit-event/<int:pk>/', views.EditEventAPIView.as_view(), name='edit-event'),
    path('past-events/', views.PastEventsAPIView.as_view(), name='past-events'),
    path('active-events/', views.ActiveEventsAPIView.as_view(), name='active-events'),
    path('upcoming-events/', views.UpcomingEventsAPIView.as_view(), name='upcoming-events'),
    path('create-withdrawal-request/', WithdrawDetailView.as_view(), name='create-withdrawal-request'),
    path('approve-withdrawal-request/<int:pk>/', views.ApproveWithdrawalRequestAPIView.as_view(), name='approve-withdrawal-request'),
    

    
]
