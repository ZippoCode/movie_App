import os

import numpy as np
import pandas as pd
from django.contrib.auth.models import User
from django.db.models import Count, Avg, Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from movies.models import Movie, UserRating, Genre
from movies.serializers import MovieSerializer
from movies.utils.recommendations import recommend


@api_view(['GET'])
def recommend_movies(request, user_id):
    similarity_path = os.path.abspath('user_similarity.npy')
    if not os.path.exists(similarity_path):
        return Response({"error": "User similarity matrix not found."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    user_similarity = np.load(similarity_path)
    ratings = pd.DataFrame(list(UserRating.objects.all().values()))
    user_movie_ratings = ratings.pivot_table(index='user_id', columns='movie_id', values='rating')
    user_movie_ratings.fillna(0, inplace=True)
    recommendations = recommend(user_id, user_movie_ratings, user_similarity)

    movie_ids = [movie_id for movie_id, _ in recommendations]
    recommended_movies = Movie.objects.filter(id__in=movie_ids)

    serializer = MovieSerializer(recommended_movies, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def user_statistics(request, user_id):
    user = get_object_or_404(User, id=user_id)

    favorite_movies = Movie.objects.filter(userpreference__user=user)
    genres = (Genre.objects.filter(movies__in=favorite_movies).annotate(num_favorites=Count('movies'))
              .order_by('-num_favorites'))
    genre_fav_stats = [{'genre': genre.name, 'count': genre.num_favorites} for genre in genres]

    user_ratings = UserRating.objects.filter(user=user)
    rated_movie_ids = user_ratings.values_list('movie_id', flat=True)
    genres = Genre.objects.filter(movies__in=Movie.objects.filter(id__in=rated_movie_ids)).annotate(
        avg_rating=Avg('movies__userrating__rating', filter=Q(movies__userrating__user=user))
    ).order_by('-avg_rating')
    genre_rated_stats = [{'genre': genre.name, 'average_rating': genre.avg_rating} for genre in genres]

    response_data = {
        'favorite_genre_statistics': genre_fav_stats,
        'rated_genre_statistics': genre_rated_stats
    }

    return Response(response_data, status=status.HTTP_200_OK)
