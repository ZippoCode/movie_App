from rest_framework import serializers

from .models import Movie, UserPreference, UserRating, Genre


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'

    def create(self, validated_data):
        movie = Movie.objects.create(**validated_data)
        return movie


class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = ['id', 'user', 'movie']
        read_only_fields = ['id']


class UserRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRating
        fields = ['user', 'movie', 'rating']
