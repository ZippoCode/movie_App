from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .apis.recommendations_api import recommend_movies, user_statistics, get_recommended_genre, \
    get_recommended_movie_by_title
from .views import MovieViewSet, add_favorite, user_favorites, UserRatingListCreate, GenreViewSet, \
    GenreRetrieveUpdateDestroy, movies_by_genre

router = DefaultRouter()
router.register(r'movies', MovieViewSet)
router.register(r'genres', GenreViewSet)

urlpatterns = [
    # API for Movies
    path('', include(router.urls)),

    # Favorites
    path('favorites/add/<int:movie_id>/', add_favorite, name='add_favorite'),
    path('favorites/', user_favorites, name='user_favorites'),

    # Ratings
    path('ratings/', UserRatingListCreate.as_view(), name='user-rating-list-create'),

    # Genres
    path('genres/<int:genre_id>/movies/', movies_by_genre, name='movies_by_genre'),

    # Recommendations
    path('recommendations/user/<int:user_id>/', recommend_movies, name='recommend_movies'),
    path('recommendations/genre/', get_recommended_genre, name='get_recommended_genre'),
    path('recommendations/title/', get_recommended_movie_by_title, name='get_recommended_movie_by_title'),

    # User Statistics
    path('user/<int:user_id>/statistics/', user_statistics, name='user_favorite_genre_statistics'),
]
