import os
import random
from pathlib import Path

import requests
from django.core.management.base import BaseCommand
from dotenv import load_dotenv

from movies.models import Genre
from movies.models import Movie

env_path = Path('') / '.env'
load_dotenv(dotenv_path=env_path)
api_key = os.getenv('APIKEY_TMDB')

GENRE_DICT = {
    28: "Action",
    12: "Adventure",
    16: "Animation",
    35: "Comedy",
    80: "Crime",
    99: "Documentary",
    18: "Drama",
    10751: "Family",
    14: "Fantasy",
    36: "History",
    27: "Horror",
    10402: "Music",
    9648: "Mystery",
    10749: "Romance",
    878: "Science Fiction",
    10770: "TV Movie",
    53: "Thriller",
    10752: "War",
    37: "Western"
}


def update_movie_with_genres(movie_id, movie_title, movie_year):
    url = f"https://api.themoviedb.org/3/search/movie"
    params = {
        'query': movie_title,
        'include_adult': 'false',
        'language': 'en-US',
        'page': 1,
        'year': movie_year,
        'api_key': api_key
    }
    headers = {
        'Authorization': f'Bearer {api_key}',
        'accept': 'application/json'
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    if not data['results']:
        print(f"No results found for {movie_title} ({movie_year})")
        return

    result = data['results'][0]
    genre_ids = result.get('genre_ids', [])
    genres = []
    for genre_id in genre_ids:
        genre_name = GENRE_DICT.get(genre_id)
        if genre_name:
            genre, created = Genre.objects.get_or_create(id=genre_id, defaults={'name': genre_name})
            genres.append(genre)
        else:
            print(f"Genre ID {genre_id} not found in GENRE_DICT")

    try:
        movie = Movie.objects.get(id=movie_id)
        movie.genres.set(genres)
        movie.save()
        print(f"Updated movie {movie.title} with genres: {[genre.name for genre in genres]}")
    except Movie.DoesNotExist:
        print(f"Movie with ID {movie_id} does not exist")


class Command(BaseCommand):
    help = 'Update genres for random movies from TMDb API'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=10, help='Number of random movies to update')

    def handle(self, *args, **options):
        count = options['count']

        movie_ids = Movie.objects.values_list('id', flat=True)
        if not movie_ids:
            self.stdout.write(self.style.ERROR('No movies found in the database'))
            return

        random_movie_ids = random.sample(list(movie_ids), min(count, len(movie_ids)))

        for movie_id in random_movie_ids:
            try:
                movie = Movie.objects.get(id=movie_id)
                movie_title = movie.title
                movie_year = movie.release_year
                update_movie_with_genres(movie_id, movie_title, movie_year)
            except Movie.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Movie with ID {movie_id} does not exist'))
