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

        modified_count = 0
        progress_bar = tqdm(total=df.shape[0], desc="Processing Movies (0 updated)")
        for _, row in df.iterrows():
            imdb_id = row.get('imdb_id')
            overview = row.get('overview')
            vote_count = row.get('vote_count')
            vote_average = row.get('vote_average')
            popularity = row.get('popularity')
            tagline = row.get('tagline')
            poster_path = row.get('poster_path')
            if not imdb_id:
                continue

            movie = Movie.objects.filter(imdb_id=imdb_id).first()

            if movie:
                movie.overview = overview if pd.notna(overview) else movie.overview
                movie.num_votes = vote_count if pd.notna(vote_count) else movie.num_votes
                movie.average_rating = vote_average if pd.notna(vote_average) else movie.average_rating
                movie.popularity = popularity if pd.notna(popularity) else movie.popularity
                movie.tagline = tagline if pd.notna(tagline) else movie.tagline
                movie.tmdb_poster_path = poster_path if pd.notna(poster_path) else movie.tmdb_poster_path
                movie.save()
                modified_count += 1
                progress_bar.set_description(f"Processing Movies ({modified_count} updated)")
            progress_bar.update(1)
        progress_bar.close()
