import os
import random
from datetime import datetime
from pathlib import Path
import requests
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from dotenv import load_dotenv
from apps.movies.models import Movie


class Command(BaseCommand):
    help = 'Fetch movies from TMDB and store them in the database'

    def handle(self, *args, **kwargs):
        # Load environment variables
        env_path = Path('') / '.env'
        load_dotenv(dotenv_path=env_path)
        APIKEY_TMDB = os.getenv('APIKEY_TMDB')

        if APIKEY_TMDB is None:
            self.stdout.write(self.style.ERROR("Not found API TMDB KEY. Exit."))
            return

        # Define API paths
        PATH_SEARCH = "https://api.themoviedb.org/3/search/movie?api_key={}&query={}"
        PATH_SIMILAR_MOVIES = 'https://api.themoviedb.org/3/movie/{}/similar?api_key={}'

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
            title = get_value(movie, 'title')
            release_year = get_value(movie, 'release_date')
            if not release_year:
                return
            overview = get_value(movie, 'overview')
            price = round(random.uniform(5.0, 50.0), 2)

            try:
                movie_obj, created = Movie.objects.get_or_create(
                    title=title,
                    release_year=release_year,
                    defaults={'overview': overview, 'price': price}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Movie added: {title} ({release_year})"))
                else:
                    self.stdout.write(self.style.SUCCESS(f"Movie already exists: {title} ({release_year})"))
            except ValidationError as e:
                self.stdout.write(self.style.ERROR(f"Validation error: {e}"))

        def fetch_and_process_similar_movies(movie_id):
            try:
                response = requests.get(PATH_SIMILAR_MOVIES.format(movie_id, APIKEY_TMDB))
                response.raise_for_status()
                similar_movies_json = response.json()

                for movie in similar_movies_json['results']:
                    process_movie(movie)
            except requests.RequestException as e:
                self.stdout.write(self.style.ERROR(f"Request error: {e}"))
            except ValidationError as e:
                self.stdout.write(self.style.ERROR(f"Validation error: {e}"))

        def store_movie(results):
            for movie in results['results']:
                process_movie(movie)
                fetch_and_process_similar_movies(movie['id'])

        try:
            while True:
                title_film = input('Enter the title of a movie: ')
                results = requests.get(PATH_SEARCH.format(APIKEY_TMDB, title_film)).json()
                store_movie(results)

        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\nKeyboardInterrupt detected. The program will exit."))
            return
