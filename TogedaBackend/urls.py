"""TogedaBackend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from reward.api.v1 import urls as reward_url
from utils import urls as utils_url
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include('user.urls')),
    path("feed/", include('feed.urls')),
    path("commerce/", include('commerce.urls')),
    path("ticket/", include('ticket.urls')),
    path("chat/", include('chat.urls')),
    path("business/", include('business.urls')),
    path("poll/", include('poll.urls')),
    path("stereo/", include('stereo.urls')),
    path("reward/", include(reward_url)),
    path("", include(utils_url))
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)