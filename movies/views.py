from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from movies.templatetags.filters import MovieFilter
from movies.models import Movie, UserPreference, UserRating, Genre
from movies.serializers import GenreSerializer, MovieSerializer, UserRatingSerializer


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    pagination_class = PageNumberPagination


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = None


class RatedMoviesView(generics.ListAPIView):
    serializer_class = MovieSerializer

    def get_queryset(self):
        account_id = self.kwargs.get('account_id')

        try:
            user = User.objects.get(id=account_id)
        except User.DoesNotExist:
            return Movie.objects.none()

        rated_movies = UserRating.objects.filter(user=user).select_related('movie')
        return [rating.movie for rating in rated_movies]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset:
            return Response({"error": "User not found or no rated movies."}, status=404)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class MovieRatingView(APIView):

    def post(self, request, movie_id):

        try:
            movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            return Response({"error": "Movie not found."}, status=404)

        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"error": "User ID is required."}, status=400)

        rating = request.data.get('rating')
        if not rating:
            return Response({"error": "Rating is required."}, status=400)
        try:
            rating, created = UserRating.objects.get_or_create(user_id=user_id, movie=movie, rating=rating)
            serializer = UserRatingSerializer(rating, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, movie_id):
        user_id = request.data.get('user_id')
        rating_value = request.data.get('rating')

        try:
            movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            return Response({"error": "Movie not found."}, status=404)

        if not user_id:
            return Response({"error": "User ID is required."}, status=400)

        try:
            rating = UserRating.objects.get(user_id=user_id, movie=movie)
        except UserRating.DoesNotExist:
            return Response({"error": "Rating not found."}, status=404)

        serializer = UserRatingSerializer(rating, data={'rating': rating_value}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, movie_id):
        user_id = request.data.get('user_id')

        try:
            movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            return Response({"error": "Movie not found."}, status=404)

        if not user_id:
            return Response({"error": "User ID is required."}, status=400)

        rating = UserRating.objects.filter(user_id=user_id, movie=movie).first()

        if rating:
            rating.delete()
            return Response({"message": "Rating deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Rating not found."}, status=status.HTTP_404_NOT_FOUND)


class GenreRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class SearchMovieView(viewsets.ReadOnlyModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = MovieFilter


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
