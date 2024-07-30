from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg
from django.db.models.signals import post_save
from django.dispatch import receiver

from movies.utils.validator import validate_rating


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=255)
    # director = models.CharField(max_length=255, blank=True, null=True)
    release_year = models.IntegerField(blank=True, null=True)
    overview = models.TextField(blank=True, null=True)
    tagline = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    genres = models.ManyToManyField(Genre, related_name='movies')
    num_votes = models.PositiveIntegerField(default=0)
    average_rating = models.FloatField(default=0.0)
    popularity = models.FloatField(default=0.0)
    imdb_id = models.CharField(max_length=255, blank=True, null=True)
    tmdb_poster_path = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ('title', 'release_year')
        constraints = [models.UniqueConstraint(fields=['title', 'release_year'], name='unique_movie')]

    def __str__(self):
        return str(self.title)

    def update_rating_stats(self):
        ratings = UserRating.objects.filter(movie=self)
        self.num_ratings = ratings.count()
        self.avg_rating = ratings.aggregate(Avg('rating'))['rating__avg'] or 0.0
        self.save()

    def get_poster_url(self):
        if self.tmdb_poster_path:
            return f"https://image.tmdb.org/t/p/w500/{self.tmdb_poster_path}"
        return None


class Person(models.Model):
    name = models.CharField(max_length=255)
    birthdate = models.DateField(blank=True, null=True)
    nationality = models.CharField(max_length=255, blank=True, null=True)
    imdb_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


class Cast(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='cast_members')
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='movie_roles')
    role = models.CharField(max_length=255)
    character_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.person.name} as {self.role} [{self.character_name}] in {self.movie.title}"


class UserPreference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'movie')

    def __str__(self):
        return f'{self.user.username} likes {self.movie.title}'


class UserRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators=[validate_rating])

    class Meta:
        unique_together = ('user', 'movie')

    def __str__(self):
        return f'{self.user.username} voted {self.movie.title} with rating {self.rating}'


@receiver(post_save, sender=UserRating)
def update_movie_ratings(sender, instance, **kwargs):
    instance.movie.update_rating_stats()
