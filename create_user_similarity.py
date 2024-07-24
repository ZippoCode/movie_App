import json
import os
import pickle

import django
import numpy as np
import pandas as pd
from django.conf import settings
from django.db.models import Prefetch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from tqdm import tqdm

from movies.utils.recommendations import build_chart

os.environ['DJANGO_SETTINGS_MODULE'] = 'movie_app.settings'
django.setup()
pd.set_option('display.max_columns', None)

from movies.models import Movie, Genre

if not os.path.exists(settings.DATASET_DIR):
    os.makedirs(settings.DATASET_DIR, exist_ok=True)
    print("Dataset directory created.")


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
        destination_filename = os.path.join(settings.DATASET_DIR, f"{genre}_movies_data.csv".lower())
        recommendations_df.to_csv(destination_filename, index=False)


def create_content_based_recommendation(filename="movies_data.csv", matrix_filename="cosine_similarity_matrix.npy",
                                        index_map_filename="movie_index_map.pkl"):
    if not os.path.exists(filename):
        create_movies_data()

    df = pd.read_csv(filename)
    df.dropna(subset=['overview'], inplace=True)

    tfidf_vectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1, 2), stop_words='english')
    tfidf_matrix = tfidf_vectorizer.fit_transform(df['overview'])
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    np.save(os.path.join(settings.DATASET_DIR, matrix_filename), cosine_sim)

    index_map = pd.Series(df.index, index=df['id']).to_dict()
    with open(os.path.join(settings.DATASET_DIR, index_map_filename), 'wb') as f:
        pickle.dump(index_map, f)

    print("Similarity matrix and index map saved.")


if __name__ == '__main__':
    # create_genre_dataset()
    create_content_based_recommendation()
