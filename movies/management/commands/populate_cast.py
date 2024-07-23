import pandas as pd
from django.core.management.base import BaseCommand
from tqdm import tqdm

from movies.models import Movie, Cast, Person


class Command(BaseCommand):
    help = 'Populate the database with movie data from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='The path of the CSV file to load')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']

        self.stdout.write(f'Loading data from {file_path}...')
        df = pd.read_csv(file_path, delimiter="\t", low_memory=False)

        # Clear DataFrame
        df = df[df['characters'] != '\\N']
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)

        for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Processing Rows"):
            t_const = row['tconst']
            n_const = row['nconst']
            category = row['category']
            character_name = row['characters']

            movie = Movie.objects.filter(imdb_id=t_const).first()
            person = Person.objects.filter(imdb_id=n_const).first()
            if movie and person:
                cast = Cast.objects.create(movie=movie, person=person, role=category, character_name=character_name)
                cast.save()

        self.stdout.write(self.style.SUCCESS('Population completed successfully.'))
