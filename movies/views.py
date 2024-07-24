import json
import os

import pandas as pd
from django.conf import settings
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from movies.utils.recommendations import build_chart
from .models import Movie
from .models import UserPreference, UserRating, Genre
from .serializers import UserRatingSerializer, GenreSerializer, MovieSerializer


class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


class UserRatingListCreate(generics.ListCreateAPIView):
    queryset = UserRating.objects.all()
    serializer_class = UserRatingSerializer


class GenreListCreate(generics.ListCreateAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class GenreRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


@api_view(['GET'])
def get_recommended_genre(request, *args, **kwargs):
    genre = request.query_params.get('genre', None)
    if not genre:
        return Response({'error': 'Genre parameter is required.'}, status=400)

    filename = f"dataset/{genre}_movies_data.csv"
    filename = os.path.join(settings.BASE_DIR, filename)
    if not os.path.isfile(filename):
        return Response({'error': 'Database not found.'}, status=500)

    recommended_df = pd.read_csv(filename)
    movie_titles = recommended_df[:15]['title'].tolist()
    movies = Movie.objects.filter(title__in=movie_titles)
    serializer = MovieSerializer(movies, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def add_favorite(request):
    username = request.data.get('username')
    movie_id = request.data.get('movie_id')

    if not username or not movie_id:
        return Response({'error': 'Username and movie_id are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(username=username)
        movie = Movie.objects.get(id=movie_id)
        UserPreference.objects.get_or_create(user=user, movie=movie)
        return Response({'message': 'Movie added to favorites'}, status=status.HTTP_201_CREATED)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Movie.DoesNotExist:
        return Response({'error': 'Movie not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def user_favorites(request):
    username = request.query_params.get('username')

    if not username:
        return Response({'error': 'Username is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(username=username)
        favorite_movies = Movie.objects.filter(userpreference__user=user)
        movie_data = [{'id': movie.id, 'title': movie.title, 'release_year': movie.release_year, 'price': movie.price}
                      for movie in favorite_movies]
        return Response({'favorites': movie_data}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


def movies_by_genre(request, genre_id):
    genre = get_object_or_404(Genre, id=genre_id)
    movies = Movie.objects.filter(genres=genre).values('id', 'title', 'release_year', 'overview', 'price')
    return JsonResponse({'genre': genre.name, 'movies': list(movies)})
