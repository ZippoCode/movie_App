import io
import logging

from django.http import HttpResponse

from movies.models import Movie
from movies.utils.generative_ai import generate_image


def generate_image_view(request):
    title = request.GET.get('title')
    if not title:
        return HttpResponse("No title provided", status=400)

    movie = Movie.objects.filter(title__exact=title).first()
    if not movie:
        return HttpResponse("Movie not found", status=404)

    overview = movie.overview
    if not overview:
        return HttpResponse("Overview not found", status=404)

    try:
        image = generate_image(title, overview)
    except Exception as e:
        logging.error(f"Error generating image: {e}")
        return HttpResponse("Error generating image", status=500)

    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='image/png')
    response['Content-Disposition'] = f'inline; filename="{title}.png"'
    return response
