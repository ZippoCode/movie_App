from django.contrib import admin

from .models import Movie, UserPreference, UserRating

admin.site.register(Movie)
admin.site.register(UserPreference)
admin.site.register(UserRating)
