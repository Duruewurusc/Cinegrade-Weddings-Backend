from rest_framework import serializers
from events.models import Package, Booking, Client, InvoiceItem, Payment, AddOn
from gallery.models import GalleryImage
from company_info.models import CompanyInfo
from users.models import Testimonial 
from djoser.serializers import UserSerializer, UserCreateSerializer
from django.contrib.auth import get_user_model


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = '__all__'

class AddOnSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddOn
        fields = '__all__'


class ClientSerializer(UserSerializer):
    trad_anniversary = serializers.DateField(required=False, allow_null=True)
    wedding_anniversary = serializers.DateField(required=False, allow_null=True)
    email = serializers.EmailField(required=True)
    class Meta(UserSerializer.Meta):
        model = get_user_model()
        # fields = ['id', 'username', 'email', 'phone']
        fields = "__all__"

class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = '__all__'
        # depth = 1




class BookingSerializer(serializers.ModelSerializer):
    total_amount= serializers.SerializerMethodField()
    total_payments_made = serializers.SerializerMethodField()
    client_name = serializers.CharField(source='client.client_name', read_only=True)
    address = serializers.CharField(source='client.address', read_only=True)
    email = serializers.CharField(source='client.email', read_only=True)
    phone = serializers.CharField(source='client.phone', read_only=True)
    # wedding_date = serializers.DateField()
    # invoice_item = serializers.CharField(source=InvoiceItemSerializer, read_only=True)

    packages_selected = PackageSerializer(many=True, read_only=True)

    class Meta:
        model = Booking
        fields = '__all__'

    def get_total_amount(self, obj):
        return obj.total_amount
    
    def get_total_payments_made(self, obj):
        return obj.total_payments_made

class PaymentSerializer(serializers.ModelSerializer):
    invoice = BookingSerializer(read_only=True)
    class Meta:
        model = Payment
        fields = '__all__'
        # depth = 1




class GallerySerializer(serializers.ModelSerializer):

    class Meta:
        model = GalleryImage
        fields = '__all__'

class CustomUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = Client
        # fields = ['id', 'username', 'email', 'first_name', 'last_name', 'address', 'phone'] 
        fields = '__all__' 

class CustomUserCreateSerializer(UserCreateSerializer):
    

    class Meta(UserCreateSerializer.Meta):
        model = Client
        fields = ['id', 'username','password', 'email', 'first_name', 'last_name', 'address', 'phone'] 
        # fields = '__all__' 

class CompanyInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyInfo
        fields = '__all__'
        

class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = '__all__'
