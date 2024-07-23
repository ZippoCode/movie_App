import pandas as pd
from django.core.management.base import BaseCommand
from tqdm import tqdm

from movies.models import Person


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

        for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Processing Rows"):
            name = row['primaryName']
            imdb_id = row["nconst"]
            person, _ = Person.objects.get_or_create(
                name=name,
                defaults={
                    'imdb_id': imdb_id
                }
            )

            person.save()

        self.stdout.write(self.style.SUCCESS('Population completed successfully.'))
