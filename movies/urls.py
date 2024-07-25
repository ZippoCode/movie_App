from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .apis.recommendations_api import recommend_movies, user_statistics, get_recommended_genre, \
    get_recommended_movie_by_title
from .views import MovieViewSet, add_favorite, UserFavoriteMoviesViewSet, RatedMoviesView, GenreViewSet, \
    MovieByGenreViewSet, SearchMovieView, MovieRatingView

router = DefaultRouter()
router.register(r'movie', MovieViewSet, basename='movie')
router.register(r'genre', GenreViewSet, basename='genre')
router.register(r'discover/movie', MovieByGenreViewSet, basename='movie-search')
router.register(r'search/movie', SearchMovieView, basename='discover_movie')
router.register(r'account/(?P<account_id>\d+)/favorite/movies', UserFavoriteMoviesViewSet,
                basename='user_favorite_movies')

urlpatterns = [
    # API for Movies
    path('', include(router.urls)),

    # Favorites
    path('favorites/add/<int:movie_id>/', add_favorite, name='add_favorite'),

    # Ratings
    path('account/<int:account_id>/rated/movies/', RatedMoviesView.as_view(), name='rated-movies'),
    path('movie/<int:movie_id>/rating/', MovieRatingView.as_view(), name='movie-rating'),

    # Recommendations
    path('recommendations/user/<int:user_id>/', recommend_movies, name='recommend_movies'),
    path('recommendations/genre/', get_recommended_genre, name='get_recommended_genre'),
    path('recommendations/title/', get_recommended_movie_by_title, name='get_recommended_movie_by_title'),

    # User Statistics
    path('user/<int:user_id>/statistics/', user_statistics, name='user_favorite_genre_statistics'),
]
