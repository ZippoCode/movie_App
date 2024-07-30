from django.urls import path

from .website_view import home, about, movie_detail_view, user_detail_view

urlpatterns = [
    path('', home, name='home'),
    path('about', about, name='about'),
    path('movie/<int:id>/', movie_detail_view, name='movie_detail'),
    path('user/', user_detail_view, name='user_detail'),

]
