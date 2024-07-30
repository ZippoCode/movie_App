from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404

from movies.models import Movie


def home(request):
    movies_list = Movie.objects.all().order_by('title')

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


# movies/views.py


def movie_detail_view(request, id):
    movie = get_object_or_404(Movie, id=id)

    return render(request, 'movie_detail.html', {'movie': movie})
