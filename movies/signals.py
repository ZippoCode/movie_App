from django.db.models import Avg
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import UserRating


@receiver(post_save, sender=UserRating)
@receiver(post_delete, sender=UserRating)
def update_movie_rating(sender, instance, **kwargs):
    movie = instance.movie
    ratings = UserRating.objects.filter(movie=movie)

    if ratings.exists():
        average_rating = ratings.aggregate(average_rating=Avg('rating'))['average_rating']
        num_votes = ratings.count()
    else:
        average_rating = 0.0
        num_votes = 0

    movie.average_rating = average_rating
    movie.num_votes = num_votes
    movie.save()
