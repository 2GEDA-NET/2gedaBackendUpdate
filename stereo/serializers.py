from rest_framework import serializers
from .models import *

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'

class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = '__all__'

class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):
    # Define serializers for related fields
    
    # Serializer for the favorite_genre field
    favorite_genre = GenreSerializer(read_only=True)
    
    # Serializer for playlists
    playlists = PlaylistSerializer(many=True, read_only=True)
    
    # Serializer for listening_history
    listening_history = SongSerializer(many=True, read_only=True)

    class Meta:
        model = UserProfile
        fields = ('user', 'favorite_genre', 'playlists', 'listening_history', 'other_profile_fields_if_any')

class StereoAccountRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StereoAccount
        fields = ['stereo_username', 'stereo_password']