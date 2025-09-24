from django.db import models
from django.contrib.auth.models import User, AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.db.models import Max

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum
from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator


class Client(AbstractUser):
    # client_name = models.CharField(max_length=100, blank=True)
    event_role = models.CharField(max_length=10, choices=[('Groom','Groom'),('Bride','Bride'),
    ('Relation','Relation'),('Planner','Planner')], blank=True)
    address= models.CharField(max_length=100, blank=True)
    instagram_handle = models.CharField(max_length=100, blank=True)
    phone = PhoneNumberField(region='NG', blank=True) 
    trad_anniversary = models.DateField(blank= True, null=True)
    wedding_anniversary = models.DateField(blank=True, null=True)
    spouse_name = models.CharField(max_length=100, blank=True)
    spouse_phone = PhoneNumberField(region='NG', blank=True) 
    spouse_email = models.EmailField( blank=True)
    spouse_instagram = models.CharField(max_length=100 , blank=True)
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'   # login with email
    REQUIRED_FIELDS = []       # no username required

    def __str__(self):
        return self.username or "Unnamed User"
    
    @property
    def client_name(self):
        return f"{self.last_name} {self.first_name}"
    




class Testimonial(models.Model):
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]

    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True, null=True)
    role_or_company = models.CharField(max_length=100, blank=True, null=True, 
                                      help_text="Person's role or company (optional)")
    content = models.TextField(help_text="The testimonial text")
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5"
    )
    image = models.ImageField(upload_to='testimonials/', blank=True, null=True,
                            help_text="Optional profile image")
    is_featured = models.BooleanField(default=False,
                                     help_text="Featured testimonials appear first")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-rating', '-created_at']
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"

    def __str__(self):
        return f"Testimonial from {self.name} ({self.get_rating_display()})"

    def stars_display(self):
        if self.rating is None:
            return "No rating"
        return '⭐' * self.rating
