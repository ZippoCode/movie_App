import random

import pandas as pd
from django.core.management.base import BaseCommand
from tqdm import tqdm

from movies.models import Movie, Genre


def clean_value(value, value_type=int):
    try:
        return value_type(value)
    except ValueError:
        return None


class Command(BaseCommand):
    help = 'Populate the database with movie data from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='The path of the CSV file to load')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']

        self.stdout.write(f'Loading data from {file_path}...')
        df = pd.read_csv(file_path, delimiter="\t", low_memory=False)

        # Clear DataFrame
        df = df[df['titleType'] == 'movie']

        df = df.dropna(subset=['primaryTitle'])
        df = df[~df['primaryTitle'].str.contains(r'^\s*episode\b', regex=True, case=False)]
        df['runtimeMinutes'] = pd.to_numeric(df['runtimeMinutes'], errors='coerce')
        df = df[df['runtimeMinutes'] >= 60]
        df = df[df['genres'] != '\\N']
        df['genres'] = df['genres'].apply(lambda x: x.split(',') if pd.notna(x) else [])
        df = df[~df['genres'].apply(lambda genres: any(genre.strip().lower() == 'short' for genre in genres))]

        df = df.sample(frac=1, random_state=42).reset_index(drop=True)

        for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Processing Rows"):
            title = row['primaryTitle']
            release_year = clean_value(row['startYear'])
            imdb_id = row["tconst"]
            genres = row['genres']

            movie, _ = Movie.objects.get_or_create(
                title=title,
                defaults={
                    'release_year': release_year,
                    'price': round(random.uniform(5.0, 50.0), 2),
                    'imdb_id': imdb_id
                }
            )

            for genre_name in genres:
                if genre_name:
                    genre, _ = Genre.objects.get_or_create(name=genre_name.strip())
                    movie.genres.add(genre)

            movie.save()

        self.stdout.write(self.style.SUCCESS('Population completed successfully.'))
