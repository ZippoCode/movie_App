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
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    genres = models.ManyToManyField(Genre, related_name='movies')
    num_votes = models.PositiveIntegerField(default=0)
    average_rating = models.FloatField(default=0.0)

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
