from django.contrib import admin
from .models import Client
from .models import Testimonial

class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'stars_display', 'is_featured', 'created_at')
    list_filter = ('is_featured', 'rating', 'created_at')
    search_fields = ('name', 'role_or_company', 'content')
    list_editable = ('is_featured',)
    readonly_fields = ('created_at', 'updated_at', 'stars_display')
    fieldsets = (
        (None, {
            'fields': ('name', 'location', 'role_or_company', 'image')
        }),
        ('Content', {
            'fields': ('content', 'rating', 'stars_display')
        }),
        ('Settings', {
            'fields': ('is_featured', 'created_at', 'updated_at')
        }),
    )

    def stars_display(self, obj):
        return obj.stars_display()
    stars_display.short_description = 'Rating'

admin.site.register(Testimonial, TestimonialAdmin)


class ClientAdmin(admin.ModelAdmin):
    list_display = ('username','client_name','phone')
    readonly_fields = ('client_name_display',)

    def client_name_display(self, obj):
        return obj.client_name
# Register your models here.
admin.site.register(Client, ClientAdmin)