import os
from datetime import datetime
from pathlib import Path

import requests
from django.core.management.base import BaseCommand
from dotenv import load_dotenv

from movies.models import Movie

# Define API paths
PATH_SEARCH = "https://api.themoviedb.org/3/search/movie?api_key={}&query={}"
MOVIE_DETAILS = "https://api.themoviedb.org/3/movie/{}?api_key={}"

PATH_SIMILAR_MOVIES = 'https://api.themoviedb.org/3/movie/{}/similar?api_key={}'

env_path = Path('') / '.env'
load_dotenv(dotenv_path=env_path)
APIKEY_TMDB = os.getenv('APIKEY_TMDB')


class Command(BaseCommand):
    help = 'Fetch movies from TMDB and store them in the database'

    def handle(self, *args, **kwargs):
        # Load environment variables

        if APIKEY_TMDB is None:
            self.stdout.write(self.style.ERROR("Not found API TMDB KEY. Exit."))
            return

        def get_value(json_object, field):
            field_value = json_object.get(field, None)
            if field == 'release_date' and field_value:
                try:
                    release_date = datetime.strptime(field_value, '%Y-%m-%d').date()
                    field_value = release_date.year
                except ValueError:
                    self.stdout.write(self.style.WARNING(f"Invalid release date: {field_value}"))
                    field_value = None
            return field_value

        def process_movie(movie):
            if movie.get('adult', True):
                return
            id = get_value(movie, 'id')
            movie_details = requests.get(MOVIE_DETAILS.format(id, APIKEY_TMDB)).json()
            imdb_id = get_value(movie_details, 'imdb_id')
            movie_obj = Movie.objects.filter(imdb_id=imdb_id).first()
            if movie_obj:
                if movie_obj.overview is None:
                    overview = get_value(movie_details, 'overview')
                    movie_obj.overview = overview if overview is not '' else None
                if movie_obj.tagline is None:
                    tagline = get_value(movie_details, 'tagline')
                    movie_obj.tagline = tagline if tagline is not '' else None
                movie_obj.save()
                self.stdout.write(self.style.SUCCESS(f"Updated {movie_obj.title}"))

        def store_movie(results):
            for movie in results['results']:
                process_movie(movie)
                # fetch_and_process_similar_movies(movie['id'])

        try:
            while True:
                title_film = input('Enter the title of a movie: ')
                results = requests.get(PATH_SEARCH.format(APIKEY_TMDB, title_film)).json()
                store_movie(results)

        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\nKeyboardInterrupt detected. The program will exit."))
            return
