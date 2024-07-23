from django.contrib import admin

from .models import Movie, UserPreference, UserRating, Genre, Person, Cast

admin.site.register(Movie)
admin.site.register(Genre)
admin.site.register(Person)
admin.site.register(Cast)
admin.site.register(UserPreference)
admin.site.register(UserRating)
