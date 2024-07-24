from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .apis.recommendations_api import recommend_movies, user_statistics, get_recommended_genre
from .views import MovieViewSet, add_favorite, user_favorites, UserRatingListCreate, GenreListCreate, \
    GenreRetrieveUpdateDestroy, movies_by_genre

router = DefaultRouter()
router.register(r'movies', MovieViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('add_favorite/<int:movie_id>/', add_favorite, name='add_favorite'),
    path('user_favorites/', user_favorites, name='user_favorites'),
    path('ratings/', UserRatingListCreate.as_view(), name='user-rating-list-create'),
    path('genres/', GenreListCreate.as_view(), name='genre-list-create'),
    path('genres/<int:pk>/', GenreRetrieveUpdateDestroy.as_view(), name='genre-detail'),
    path('genres/<int:genre_id>/movies/', movies_by_genre, name='movies_by_genre'),
    path('recommendations/<int:user_id>/', recommend_movies, name='recommend_movies'),
    path('recommendations/genre/', get_recommended_genre, name='movie-recommendations'),
    path('user/<int:user_id>/statistics/', user_statistics, name='user_favorite_genre_statistics'),
]
