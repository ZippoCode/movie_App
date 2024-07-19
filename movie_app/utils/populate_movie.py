# populate_films.py
import os

import django

from movie_app.apps.movies.models import Movie

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mymovieapp.settings')
django.setup()


def populate():
    movies = [
        {'title': 'Film A', 'director': 'Director A', 'release_year': 2020, 'price': 19.99, 'rating': 4.5},
        {'title': 'Film B', 'director': 'Director B', 'release_year': 2021, 'price': 24.99, 'rating': 4.0},
    ]

    for movie_data in movies:
        movie, created = Movie.objects.get_or_create(**movie_data)
        if created:
            print(f"Created: {movie.title}")
        else:
            print(f"Already exists: {movie.title}")


if __name__ == '__main__':
    populate()
