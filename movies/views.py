from django.contrib.auth.models import User
from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Movie, UserPreference, UserRating, Genre
from .serializers import UserRatingSerializer, GenreSerializer, MovieSerializer


class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    pagination_class = PageNumberPagination


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = None


class UserRatingListCreate(generics.ListCreateAPIView):
    queryset = UserRating.objects.all()
    serializer_class = UserRatingSerializer
    pagination_class = PageNumberPagination


class GenreRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class SearchMovieView(APIView):
    def get(self, request, *args, **kwargs):
        title = request.query_params.get('title', None)
        if not title:
            return Response({'error': 'Title is required'}, status=status.HTTP_400_BAD_REQUEST)

        movies = Movie.objects.filter(title__icontains=title)
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MovieByGenreViewSet(viewsets.ViewSet):

    @staticmethod
    def list(request):
        genre_id = request.query_params.get('genre_id')
        genre_name = request.query_params.get('genre_name')

        if genre_id:
            try:
                genre = Genre.objects.get(id=genre_id)
            except Genre.DoesNotExist:
                raise NotFound(detail="Genre not found.")
            movies = Movie.objects.filter(genres=genre)
        elif genre_name:
            try:
                genre = Genre.objects.get(name__iexact=genre_name)
            except Genre.DoesNotExist:
                raise NotFound(detail="Genre not found.")
            movies = Movie.objects.filter(genres=genre)
        else:
            return Response({"error": "Please provide either 'genre_id' or 'genre_name'."}, status=400)

        if not movies.exists():
            return Response({"message": "No movies found for the given genre."}, status=404)

        paginator = PageNumberPagination()
        paginated_movies = paginator.paginate_queryset(movies, request)

        serializer = MovieSerializer(paginated_movies, many=True)
        return paginator.get_paginated_response(serializer.data)


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


class UserFavoriteMoviesViewSet(viewsets.ViewSet):

    @staticmethod
    def list(request, account_id=None):
        if not account_id:
            return Response({'error': 'Account ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=account_id)
            favorite_movies = Movie.objects.filter(userpreference__user=user)

            paginator = PageNumberPagination()
            paginated_movies = paginator.paginate_queryset(favorite_movies, request)
            serializer = MovieSerializer(paginated_movies, many=True)
            return paginator.get_paginated_response(serializer.data)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
