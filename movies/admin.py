from django.contrib import admin

from .models import Movie, UserPreference, UserRating, Genre

admin.site.register(Movie)
admin.site.register(UserPreference)
admin.site.register(UserRating)
admin.site.register(Genre)
