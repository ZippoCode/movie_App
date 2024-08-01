from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect

from movies.models import Movie, UserRating


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


def user_detail_view(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('login')
    user_ratings = UserRating.objects.filter(user=request.user).select_related('movie').order_by('-rating')[:10]

    return render(request, 'user_detail.html', {'user': user, 'user_ratings': user_ratings})


from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.forms import AuthenticationForm


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
