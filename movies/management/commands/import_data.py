import pandas as pd
from django.core.management.base import BaseCommand
from tqdm import tqdm

from movies.models import Movie


class Command(BaseCommand):
    help = 'Import movies from a CSV file using pandas'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file containing movie data')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        df = pd.read_csv(csv_file, low_memory=False)

        for _, row in tqdm(df.iterrows(), total=df.shape[0], desc="Processing Movie"):
            imdb_id = row.get('imdb_id')
            overview = row.get('overview')

            movie = Movie.objects.filter(imdb_id=imdb_id).first()

            if movie:
                movie.overview = overview if pd.notna(overview) else movie.overview
                movie.save()
