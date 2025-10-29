from rest_framework import serializers
from events.models import Package, Booking, Client, InvoiceItem, Payment, AddOn, BookingDate
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


class BookingDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingDate
        fields = ['id', 'date']

class BookingSerializer(serializers.ModelSerializer):
    event_dates = BookingDateSerializer(many=True, required=False)
    total_amount= serializers.SerializerMethodField()
    total_payments_made = serializers.SerializerMethodField()
    client_name = serializers.CharField(source='client.client_name', read_only=True)
    address = serializers.CharField(source='client.address', read_only=True)
    email = serializers.CharField(source='client.email', read_only=True)
    phone = serializers.CharField(source='client.phone', read_only=True)
 
    class Meta:
        model = Booking
        fields = '__all__'

    def get_total_amount(self, obj):
        return obj.total_amount
    
    def get_total_payments_made(self, obj):
        return obj.total_payments_made
    

    def create(self, validated_data):
        packages = validated_data.pop('packages', [])
        addons = validated_data.pop('Addons', [])
        event_dates_data = validated_data.pop('event_dates', [])
        
        booking = Booking.objects.create(**validated_data)
        

           # Now attach the M2M relations properly
        booking.packages.set(packages)
        booking.Addons.set(addons)
        # Create event dates
        for event_date_data in event_dates_data:
            BookingDate.objects.create(booking=booking, **event_date_data)
        
        return booking

    def update(self, instance, validated_data):
        event_dates_data = validated_data.pop('event_dates', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if event_dates_data is not None:
            instance.event_dates.all().delete()
            for event_date_data in event_dates_data:
                BookingDate.objects.create(booking=instance, **event_date_data)

        return instance




    
    # def create(self, validated_data):
    #     dates_data = validated_data.pop('dates', [])
    #     booking = Booking.objects.create(**validated_data)
    #     for date_data in dates_data:
    #         BookingDate.objects.create(booking=booking, **date_data)
    #     return booking

    # def update(self, instance, validated_data):
    #     dates_data = validated_data.pop('dates', None)

    #     for attr, value in validated_data.items():
    #         setattr(instance, attr, value)
    #     instance.save()

    #     if dates_data is not None:
    #         instance.dates.all().delete()
    #         for date_data in dates_data:
    #             BookingDate.objects.create(booking=instance, **date_data)

    #     return instance



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
