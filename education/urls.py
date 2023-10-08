from django.urls import path, include
from . views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register('admin-universities-views', AdminPastQuestionViewSet, basename='admin-view')
router.register('universities', UniversitiesViewSet)
router.register('user-universities-views', UserPastQuestionViewSet, basename='user-views')

urlpatterns = [
    path('', include(router.urls)),
]
