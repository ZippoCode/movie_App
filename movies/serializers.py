from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Movie, UserPreference, UserRating, Genre


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'

    def create(self, validated_data):
        genres_data = validated_data.pop('genres', [])
        movie = Movie.objects.create(**validated_data)
        for genre_data in genres_data:
            print(genre_data)
            genre, created = Genre.objects.get_or_create(**genre_data)
            movie.genres.add(genre)
        return movie


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = ['id', 'user', 'movie']
        read_only_fields = ['id']


class UserRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRating
        fields = ['user', 'movie', 'rating']
        read_only_fields = ['user', 'movie']
