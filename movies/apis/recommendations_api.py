import os
import pickle

import numpy as np
import pandas as pd
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Count, Avg, Q
from django.http import JsonResponse
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


@api_view(['GET'])
def get_recommended_genre(request, *args, **kwargs):
    genre_name = request.query_params.get('name', None)
    if not genre_name:
        return Response({'error': 'Genre parameter is required.'}, status=400)

    genre_name = genre_name.capitalize()
    if not Genre.objects.filter(name=genre_name).exists():
        return Response({'error': 'Genre not found.'}, status=401)

    filename = os.path.join(settings.DATASET_DIR, f"{genre_name}_movies_data.csv")
    if not os.path.isfile(filename):
        return Response({'error': 'Database not found.'}, status=500)

    recommended_df = pd.read_csv(filename)
    movie_titles = recommended_df[:15]['title'].tolist()
    movies = Movie.objects.filter(title__in=movie_titles)
    serializer = MovieSerializer(movies, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_recommended_movie_by_title(request):
    title = request.query_params.get('title', None)
    if not title:
        return JsonResponse({'error': 'Title parameter is required.'}, status=400)

    title = title.title()
    matrix_filename = os.path.join(settings.DATASET_DIR, "cosine_similarity_matrix.npy")
    index_map_filename = os.path.join(settings.DATASET_DIR, "movie_index_map.pkl")

    if not os.path.isfile(matrix_filename) or not os.path.isfile(index_map_filename):
        return JsonResponse({'error': 'Data files not found.'}, status=500)

    cosine_sim = np.load(matrix_filename)
    with open(index_map_filename, 'rb') as f:
        index_map = pickle.load(f)

    movies_df = pd.DataFrame(list(Movie.objects.values('id', 'title', 'overview')))
    movies_df['title'] = movies_df['title'].str.title()  # Normalize the title format

    if title not in movies_df['title'].values:
        return JsonResponse({'error': f'Movie with title {title} not found.'}, status=404)

    # Retrieve the movie ID and use the index map to get the corresponding index
    movie_id = movies_df[movies_df['title'] == title]['id'].values[0]
    idx = index_map.get(movie_id, None)

    if idx is None:
        return JsonResponse({'error': f'Movie with title {title} not in similarity matrix.'}, status=404)

    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]  # Get top 10 recommendations
    movie_indices_list = [i[0] for i in sim_scores]

    # Use the indices from the similarity matrix to get recommended movies
    recommended_movies = movies_df.iloc[movie_indices_list].to_dict('records')

    return JsonResponse(recommended_movies, safe=False, status=200)
