from django.db import models

# Create your models here.
from django.db import models
from django.utils.text import slugify

class GalleryImage(models.Model):
    title = models.CharField(max_length=200, unique=False, blank=True)
    src = models.ImageField(upload_to='gallery/')
    category = models.CharField(max_length=100, choices=[
        ('wedding', 'Wedding'),
        ('engagement', 'Engagement'),
        ('portrait', 'Portrait'),
        ('funeral', 'Funeral'),
        ('others', 'Others'),
    ])
    date_taken = models.DateField(blank=True, null=True)
    slug = models.SlugField(max_length=200, unique=False, blank=True)
    featured = models.BooleanField(default=False)
    
    # def save(self, *args, **kwargs):
    #     if not self.slug:
    #         self.slug = slugify(f"{self.title}-{self.date_taken}")
    #     super().save(force_insert=True *args, kwargs)
    
    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-date_taken']