from django.contrib.auth.models import User
from django.db import models


class Movie(models.Model):
    title = models.CharField(max_length=255)
    # director = models.CharField(max_length=255, blank=True, null=True)
    release_year = models.IntegerField(blank=True, null=True)
    overview = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)

    # genres = models.ManyToManyField(Genre, related_name="genres", blank=True, null=True)

    class Meta:
        unique_together = ('title', 'release_year')
        constraints = [models.UniqueConstraint(fields=['title', 'release_year'], name='unique_movie')]

    def __str__(self):
        return str(self.title)


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
    rating = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ('user', 'movie')

    def __str__(self):
        return f'{self.user.username} voted {self.movie.title} with rating {self.rating}'
