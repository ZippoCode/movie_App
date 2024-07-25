# movies/filters.py

import django_filters

from .models import Movie, Genre


class MovieFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    release_year = django_filters.NumberFilter()
    overview = django_filters.CharFilter(lookup_expr='icontains')
    tagline = django_filters.CharFilter(lookup_expr='icontains')
    price = django_filters.NumberFilter()
    num_votes = django_filters.NumberFilter()
    average_rating = django_filters.NumberFilter()
    popularity = django_filters.NumberFilter()
    imdb_id = django_filters.CharFilter(lookup_expr='icontains')
    genres = django_filters.ModelMultipleChoiceFilter(queryset=Genre.objects.all(), to_field_name='name')

    class Meta:
        model = Movie
        fields = ['title', 'release_year', 'overview', 'tagline', 'price', 'num_votes', 'average_rating', 'popularity',
                  'imdb_id', 'genres']
