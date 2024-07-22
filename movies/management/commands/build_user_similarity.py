import os
import sqlite3

import numpy as np
import pandas as pd
from django.core.management.base import BaseCommand
from sklearn.metrics.pairwise import cosine_similarity


class Command(BaseCommand):
    help = 'Build user similarity matrix and save it'

    def handle(self, *args, **kwargs):
        database_path = os.path.abspath('db.sqlite3')
        connection = sqlite3.connect(database_path)

        try:
            ratings = pd.read_sql_query("SELECT * FROM movies_userrating", connection)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading tables: {e}"))
            connection.close()
            return

        user_movie_ratings = ratings.pivot_table(index='user_id', columns='movie_id', values='rating')
        user_movie_ratings.fillna(0, inplace=True)

        user_similarity = cosine_similarity(user_movie_ratings)

        similarity_path = os.path.abspath('user_similarity.npy')
        np.save(similarity_path, user_similarity)
        self.stdout.write(self.style.SUCCESS(f"User similarity matrix saved to {similarity_path}"))

        connection.close()
