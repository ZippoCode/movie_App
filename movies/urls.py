from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import MovieViewSet, add_favorite, user_favorites

router = DefaultRouter()
router.register(r'movies', MovieViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('add_favorite/<int:movie_id>/', add_favorite, name='add_favorite'),
    path('user_favorites/', user_favorites, name='user_favorites'),
]
