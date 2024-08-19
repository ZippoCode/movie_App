from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.views import View
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from movies.models import Movie
from movies.models import UserRating
from movies.serializers import UserSerializer, UserRatingSerializer


def home(request):
    movies_list = Movie.objects.all().order_by('popularity')

    paginator = Paginator(movies_list, 10)
    page = request.GET.get('page', 1)

    try:
        movies = paginator.page(page)
    except PageNotAnInteger:
        movies = paginator.page(1)
    except EmptyPage:
        movies = paginator.page(paginator.num_pages)

    return render(request, 'home.html', {'movies': movies})


def about(request):
    return render(request, 'about.html')


def movie_detail_view(request, id):
    movie = get_object_or_404(Movie, id=id)

    return render(request, 'movie_detail.html', {'movie': movie})


class UserDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Ottieni tutte le valutazioni dell'utente
        user_ratings = UserRating.objects.filter(user=user)

        # Serializza i dati utente
        user_serializer = UserSerializer(user)

        # Serializza i dati delle valutazioni dell'utente
        ratings_serializer = UserRatingSerializer(user_ratings, many=True)

        # Combina i dati utente e le valutazioni in una singola risposta
        response_data = {
            'user': user_serializer.data,
            'ratings': ratings_serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)


class CustomLoginView(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'registration/login.html', {'form': form})

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to the home page or any other page
        return render(request, 'registration/login.html', {'form': form})
