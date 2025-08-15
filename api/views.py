from django.shortcuts import render
from rest_framework.decorators import api_view

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework.response import Response
from rest_framework import status
from .serializers import PackageSerializer, TestimonialSerializer, ClientSerializer, BookingSerializer, GallerySerializer, PaymentSerializer, AddOnSerializer, CompanyInfoSerializer, InvoiceItemSerializer
from events.models import Package, Booking, InvoiceItem, Payment, AddOn
from users.models import Client, Testimonial
from gallery.models import GalleryImage
from company_info.models import CompanyInfo


# Create your views here.

class PackageViewSet(viewsets.ModelViewSet):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [AllowAny]

class AddOnViewSet(viewsets.ModelViewSet):
    queryset = AddOn.objects.all()
    serializer_class = AddOnSerializer
    permission_classes = [AllowAny]


class UserViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [AllowAny]


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = self.request.user
        print(user)
        if user.is_staff or user.is_superuser:
            return Booking.objects.all().order_by('-wedding_date')
        return Booking.objects.filter(client=user).order_by('-wedding_date')
    
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = self.request.user
        print(user)
        if user.is_staff or user.is_superuser:
            return Payment.objects.all().order_by('-payment_date')
        return Payment.objects.filter(invoice__client =user).order_by('-payment_date')

class GalleryViewSet(viewsets.ModelViewSet):
    queryset = GalleryImage.objects.all()
    serializer_class = GallerySerializer
    permission_classes = [AllowAny]


class CompanyInfoViewSet(viewsets.ModelViewSet):
    queryset = CompanyInfo.objects.all()
    serializer_class = CompanyInfoSerializer
    permission_classes = [AllowAny]

class InvoiceItemViewSet(viewsets.ModelViewSet):
    queryset = InvoiceItem.objects.all()
    serializer_class = InvoiceItemSerializer
    permission_classes = [AllowAny]

class TestimonialViewSet(viewsets.ModelViewSet):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer
    permission_classes = [AllowAny]