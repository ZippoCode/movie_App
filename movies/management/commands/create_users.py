import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from movies.models import Movie, UserPreference, UserRating


class Command(BaseCommand):
    help = 'Create 50 users with username and password as UserNumber<index> and assign random favorite movies'

    def add_arguments(self, parser):
        parser.add_argument(
            '--movies-only',
            action='store_true',
            help='If set, only movies will be saved, not users'
        )

    def handle(self, *args, **kwargs):
        movies_only = kwargs['movies_only']

        if not movies_only:
            users = []
            for i in range(1, 51):
                username = f'User{i}'
                password = username
                email = f'{username}@example.com'

                user = User(
                    username=username,
                    email=email
                )
                user.set_password(password)
                users.append(user)

                self.stdout.write(self.style.SUCCESS(f'Created user {username}'))

            User.objects.bulk_create(users)
            self.stdout.write(self.style.SUCCESS('Successfully created 50 users'))

        movies = list(Movie.objects.all())
        user_ids = list(User.objects.values_list('id', flat=True))

        preferences = []
        ratings_data = []

        for user_id in user_ids:
            if not movies:
                self.stdout.write(self.style.WARNING(f'No movies available for user {user_id}'))
                continue

            # Randomly shuffle movies
            shuffled_movies = random.sample(movies, len(movies))

            # Split movies into two parts
            num_movies = len(shuffled_movies)
            split_point = num_movies // 2

            # First half for preferences, second half for ratings
            preference_movies = shuffled_movies[:split_point]
            rating_movies = shuffled_movies[split_point:]

            for movie in preference_movies:
                if not UserPreference.objects.filter(user_id=user_id, movie=movie).exists():
                    preferences.append(UserPreference(user_id=user_id, movie=movie))
                    self.stdout.write(self.style.SUCCESS(f'User {user_id} added favorite movie {movie.title}'))

            for movie in rating_movies:
                if not UserRating.objects.filter(user_id=user_id, movie=movie).exists():
                    rating = random.randint(1, 5)
                    ratings_data.append(UserRating(user_id=user_id, movie=movie, rating=rating))
                    self.stdout.write(self.style.SUCCESS(f'User {user_id} rated movie {movie.title} with {rating}'))

        # Bulk create preferences and ratings
        UserPreference.objects.bulk_create(preferences)
        UserRating.objects.bulk_create(ratings_data)
        self.stdout.write(self.style.SUCCESS('Successfully added preferences and ratings'))
