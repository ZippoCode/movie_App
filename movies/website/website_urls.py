from django.contrib.auth import views as auth_views
from django.urls import path

from .website_view import home, about, movie_detail_view, UserDetailView, CustomLoginView

urlpatterns = [
    path('', home, name='home'),
    path('about', about, name='about'),
    path('movie/<int:id>/', movie_detail_view, name='movie_detail'),
    path('user/', UserDetailView.as_view(), name='user_detail'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

]
