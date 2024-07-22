import pandas as pd
from django.core.management.base import BaseCommand

from movies.models import Movie, Genre


class Command(BaseCommand):
    help = 'Populate the database with movie data from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='The path of the CSV file to load')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']

        def clean_value(value, value_type=int):
            try:
                return value_type(value)
            except ValueError:
                return None

        self.stdout.write(f'Loading data from {file_path}...')
        df = pd.read_csv(file_path, delimiter="\t", low_memory=True)

        for index, row in df.iterrows():
            title = row['primaryTitle']
            release_year = clean_value(row['startYear'])
            genres = row['genres'].split(',') if pd.notna(row['genres']) else []

            movie, created = Movie.objects.get_or_create(
                title=title,
                defaults={
                    'release_year': release_year,
                    'overview': '',
                    'price': None
                }
            )

            if created:
                self.stdout.write(f'Created new movie: {title}')
            else:
                self.stdout.write(f'Updated existing movie: {title}')

            for genre_name in genres:
                if genre_name:
                    genre, _ = Genre.objects.get_or_create(name=genre_name.strip())
                    movie.genres.add(genre)

            movie.save()

        self.stdout.write(self.style.SUCCESS('Population completed successfully.'))
