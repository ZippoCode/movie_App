import os
import random
from datetime import datetime

import django
import requests
from django.core.exceptions import ValidationError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie_app.settings')
django.setup()

from movie_app.apps.movies.models import Movie

APIKEY_TMDB = "dd8353ae5ad8d568675bf7703a9a84c5"
PATH_SEARCH = "https://api.themoviedb.org/3/search/movie?api_key={}&query={}"
PATH_SIMILAR_MOVIES = 'https://api.themoviedb.org/3/movie/{}/similar?api_key={}'
PATH_MOVIES = "https://api.themoviedb.org/3/movie/{}?api_key={}"
PATH_KEYWORDS = 'https://api.themoviedb.org/3/movie/{}/keywords?api_key={}'
PATH_CREDITS = "https://api.themoviedb.org/3/movie/{}/credits?api_key={}"
PATH_PERSON = 'https://api.themoviedb.org/3/person/{}?api_key={}'


def get_value(json_object, field):
    return json_object[field] if field in json_object else None


def store_move(movie):
    if movie.get('adult', True):
        return None
    title = get_value(movie, 'title')
    release_date_str = get_value(movie, 'release_date')
    overview = get_value(movie, 'overview')

    release_date = None
    if release_date_str:
        try:
            release_date = datetime.strptime(release_date_str, '%Y-%m-%d').date()
        except ValueError:
            print(f"Data di rilascio non valida: {release_date_str}")
            return None

    price = round(random.uniform(5.0, 50.0), 2)

    movie_values = {
        'title': title,
        'release_date': release_date,
        'overview': overview,
        'price': price
    }

    try:
        film, created = Movie.objects.get_or_create(
            title=title,
            defaults=movie_values
        )
        if not created:
            for key, value in movie_values.items():
                setattr(film, key, value)
            film.save()
        return film
    except ValidationError as e:
        print(f"Errore di validazione: {e}")
        return None


if __name__ == '__main__':
    while True:
        title_film = input('Inserisci il titolo di un movie: ')
        request_json = (requests.get(PATH_SEARCH.format(APIKEY_TMDB, title_film))).json()
        for movie in request_json['results']:
            store_move(movie)
    sys.exit()
