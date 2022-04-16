from django.shortcuts import render
from .models import Video


def index(request):
    video = Video.objects.all()
    context = {
        'video': video
    }
    return render(request, 'video/show.html', context)
# Create your views here.
