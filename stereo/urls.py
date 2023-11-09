# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'genres', GenreViewSet)
router.register(r'userprofiles', UserProfileViewSet)
router.register(r'playlists', PlaylistViewSet)
router.register(r'artists', ArtistViewSet)
router.register(r'songs', SongViewSet)
router.register(r'stream-count', StreamCountViewset, basename='stream-count')


urlpatterns = [
    path('api/', include(router.urls)),
    # Add other URL patterns here as needed.
    path('stereo/register/', StereoAccountRegistrationView.as_view(), name='stereo_account_register'),
    path('stereo/login/', StereoAccountLoginView.as_view(), name='stereo_account_login'),
    path('quick-pick-songs/', QuickPickSongsAPIView.as_view(), name='quick_pick_songs_api'),
    path('top-albums/', TopAlbumsAPIView.as_view(), name='top_albums_api'),
    path('download-song/<int:song_id>/', download_song, name='download_song'),
    path('songs-by-album/<str:album_name>/', SongsByAlbumAPIView.as_view(), name='songs_by_album_api'),
    path('songs-by-genre/<str:genre_name>/', SongsByGenreAPIView.as_view(), name='songs_by_genre_api'),
    path('songs/<int:song_id>/like_dislike/', LikeDislikeSongView.as_view(), name='like_dislike_song'),
    path('top-songs-by-artist/<str:artist_name>/', TopSongsByArtistAPIView.as_view(), name='top-songs-by-artist'),
    path('songs/upload/', ArtistSongUploadView.as_view(), name='artist-song-upload'),
    path('songs/<int:pk>/delete/', DeleteSongView.as_view(), name='delete-song'),
    path('search/', SongSearchView.as_view(), name='song-search'),
    path('artists/search/', ArtistSearchView.as_view(), name='artist-search'),
    path('user_downloads/', UserDownloadsList.as_view(), name='user_downloads_list'),
    path('playlist-count/', PlaylistCountView.as_view(), name='playlist-count'),



]
