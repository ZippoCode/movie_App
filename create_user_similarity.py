import json
import os

import django
import pandas as pd
from django.db.models import Prefetch
from tqdm import tqdm

from movies.utils.recommendations import build_chart

os.environ['DJANGO_SETTINGS_MODULE'] = 'movie_app.settings'
django.setup()
pd.set_option('display.max_columns', None)

from movies.models import Movie, Genre

DATASET_DIR = 'dataset'
os.makedirs(DATASET_DIR, exist_ok=True)


def create_movies_data(filename="movies_data.csv"):
    filename = os.path.join(filename)
    if not os.path.exists(filename):
        movies = Movie.objects.prefetch_related(Prefetch('genres'))
        data = []

        for movie in tqdm(movies.iterator(), total=movies.count(), desc="Processing Movies"):
            movie_data = movie.__class__.objects.filter(pk=movie.pk).values().first()
            movie_data['genres'] = [genre.name for genre in movie.genres.all()]
            data.append(movie_data)

        df = pd.DataFrame(data)
        df['genres'] = df['genres'].apply(json.dumps)
        df.to_csv(filename, index=False)
    else:
        df = pd.read_csv(filename)
        df['genres'] = df['genres'].apply(json.loads)


def create_genre_dataset(filename="movies_data.csv"):
    if not os.path.exists(filename):
        create_movies_data()
    genres = Genre.objects.values_list('name', flat=True).distinct()
    df = pd.read_csv(filename)
    df['genres'] = df['genres'].apply(json.loads)
    for genre in tqdm(genres, total=genres.count()):
        recommendations_df = build_chart(df, genre, 1000)
        destination_filename = os.path.join(DATASET_DIR, f"{genre}_movies_data.csv")
        recommendations_df.to_csv(destination_filename, index=False)


if __name__ == '__main__':
    create_genre_dataset()
