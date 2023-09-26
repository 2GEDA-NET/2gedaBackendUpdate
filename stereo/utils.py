# utils.py

from .models import Song

def update_top_tracks():
    N = 10  # Number of top tracks to maintain

    # Get the top N downloaded songs
    top_downloaded_songs = Song.objects.order_by('-download_count')[:N]

    # Get the top N streamed songs
    top_streamed_songs = Song.objects.order_by('-stream_count')[:N]

    # Combine the top downloaded and streamed songs
    top_songs = set(top_downloaded_songs) | set(top_streamed_songs)

    # Update the is_top_track field for these songs
    for song in top_songs:
        song.is_top_track = True
        song.save()
