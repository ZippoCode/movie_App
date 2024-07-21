from django.contrib.auth.models import User
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Movie, Genre, UserPreference
from .serializers import MovieSerializer, GenreSerializer


class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


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
