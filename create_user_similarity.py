import os

import django
import numpy as np
import pandas as pd
from django.db.models import Prefetch
from tqdm import tqdm

os.environ['DJANGO_SETTINGS_MODULE'] = 'movie_app.settings'
django.setup()

from movies.models import Movie


def build_measure(df: pd.DataFrame):
    vote_counts = df[df['num_votes'].notnull()]['num_votes'].astype('int')
    vote_averages = df[df['average_rating'].notnull()]['average_rating'].astype('int')
    c = vote_averages.mean()
    m = vote_counts.quantile(0.95)
    return c, m


def create_user_similarity(filename="movies_data.csv"):
    if not os.path.exists(filename):
        movies = Movie.objects.prefetch_related(Prefetch('genres'))
        data = []

        for movie in tqdm(movies.iterator(), total=movies.count(), desc="Processing Movies"):
            movie_data = movie.__class__.objects.filter(pk=movie.pk).values().first()
            genre_names = [genre.name for genre in movie.genres.all()]
            movie_data['genres'] = ', '.join(genre_names)
            data.append(movie_data)

        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
    else:
        df = pd.read_csv(filename)

    average_rating, mean_rating = build_measure(df)
    print(average_rating, mean_rating)


if __name__ == '__main__':
    create_user_similarity()
