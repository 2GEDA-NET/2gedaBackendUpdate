# filters.py
import django_filters
from .models import *

class SongFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains')

    class Meta:
        model = Song
        fields = ['title', 'genre']  # Add more fields if needed

class ArtistFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Artist
        fields = ['name', 'about']  # Add more fields if needed