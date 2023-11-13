from .views import Download, Add_Watermark, Add_Watermark_video
from django.urls import path


urlpatterns = [
    path('download', Download.as_view()),
    path('watermark/<path:filepath>/', Add_Watermark),
    path('download-video/<path:filepath>/', Add_Watermark_video)
]
