from rest_framework import serializers

from .models import Movie, Genre


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'


class MovieSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    genre_names = serializers.ListField(child=serializers.CharField(), write_only=True)

    class Meta:
        model = Movie
        fields = '__all__'

    def create(self, validated_data):
        genre_names = validated_data.pop('genre_names')
        movie = Movie.objects.create(**validated_data)
        genres = [Genre.objects.get_or_create(name=name)[0] for name in genre_names]
        movie.genres.set(genres)
        return movie
