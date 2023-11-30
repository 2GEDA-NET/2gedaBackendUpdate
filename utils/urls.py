from .views import Download, Add_Watermark, Add_Watermark_video
from django.urls import path
from .views import(
    GeographyAPIView,
    UserGeographyView
)


urlpatterns = [
    path('download', Download.as_view()),
    path('watermark/<path:filepath>/', Add_Watermark),
    path('download-video/<path:filepath>/', Add_Watermark_video),
    path('geography/', GeographyAPIView.as_view()),
    path('user/geography/', UserGeographyView.as_view()),
]
