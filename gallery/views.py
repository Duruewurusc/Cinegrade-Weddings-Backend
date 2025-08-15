from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from .models import GalleryImage

def gallery_view(request):
    images = GalleryImage.objects.all()
    categories = GalleryImage.objects.values_list('category', flat=True).distinct()
    
    context = {
        'images': images,
        'categories': categories,
    }
    return render(request, 'gallery.html', context)