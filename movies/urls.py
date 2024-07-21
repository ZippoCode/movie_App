from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import MovieViewSet, add_favorite, user_favorites, UserRatingListCreate, GenreListCreate, \
    GenreRetrieveUpdateDestroy, movies_by_genre

router = DefaultRouter()
router.register(r'movies', MovieViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('add_favorite/<int:movie_id>/', add_favorite, name='add_favorite'),
    path('user_favorites/', user_favorites, name='user_favorites'),
    path('api/ratings/', UserRatingListCreate.as_view(), name='user-rating-list-create'),
    path('api/genres/', GenreListCreate.as_view(), name='genre-list-create'),
    path('api/genres/<int:pk>/', GenreRetrieveUpdateDestroy.as_view(), name='genre-detail'),
    path('api/genres/<int:genre_id>/movies/', movies_by_genre, name='movies_by_genre'),
]
