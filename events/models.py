from django.db import models
from django.contrib.auth.models import User, AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.db.models import Max

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum


from users.models import Client

class Package(models.Model):
    package_name = models.CharField(max_length=100)
    event_type = models.CharField(max_length=10, choices=[('wedding','wedding'),('burial','burial'),('birthday','birthday'),('corporate','coroprate'),('custom','custom')], default='wedding', null=True, blank=True,)
    category = models.CharField(max_length=10, choices=[('photo','photo'),('video','video'),('combo','combo'),('custom','custom')], default='combo')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    deliverables = models.TextField(help_text="List of deliverables, separated by commas")
    duration = models.CharField(max_length=50, help_text="E.g., '8 hours coverage'", blank=True)
    is_popular = models.BooleanField(default=False)
    image = models.ImageField(upload_to='package_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['price']

    def __str__(self):
        return f"{self.package_name} (+N{self.price})"

    def deliverables_list(self):
        return [d.strip() for d in self.deliverables.split(',')]
    
    class Meta:
        ordering = ['price']
        verbose_name = 'Event Package'
        verbose_name_plural = 'Event Packages'

class AddOn(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10,decimal_places=2, validators=[MinValueValidator(0)])  
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} (+N{self.price})"

  
    
    
class Booking(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PART_PAYMENT = 'confirmed', 'Confirmed'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    class DeliveryStatus(models.TextChoices):
        UP_COMING = 'Up Coming', 'Up Coming'
        IN_PROGRESS = 'In progress','In progress'
        READY = 'Ready', 'Ready'
        DELIVERED = 'Delivered', 'Delivered'

    class EventType(models.TextChoices):
        WEDDING = 'Wedding', 'Wedding'
        TRADITIONAL_MARRIAGE = 'Traditional Marriage', 'Traditional Marriage'
        PREWEDDING_SHOOT = 'Prewedding Shoot','Prewedding Shoot',
        BURIAL = 'Burial', 'Burial'
        BIRTHDAY = 'Birthday', 'Birthday'
        OTHERS = 'Others','Others'

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='booker', default="")
    event_type = models.CharField(max_length=255, choices=EventType.choices, blank=True, null=True)
    event_description = models.CharField(max_length=255, blank=True, null=True)
    wedding_date = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True )
    packages = models.ManyToManyField(Package, related_name='bookings', blank=True)
    Addons = models.ManyToManyField(AddOn, related_name='package_addon', blank=True)
    additional_notes = models.TextField(blank=True, null=True)
    date_booked = models.DateTimeField(auto_now_add=True)
    booking_code = models.CharField(max_length=20, unique=True, editable=False, blank=True)
    invoice_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    issue_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    # Payments
    amount_due = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True, default=0)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING, null=True)
    tax_rate = models.DecimalField(max_digits=5,decimal_places=2, default=0,validators=[MinValueValidator(0)])
    delivery_status = models.CharField(max_length=50,choices=DeliveryStatus.choices, default=DeliveryStatus.IN_PROGRESS)
    Image_link = models.URLField(blank=True, null=True)
    Video_link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True )
    updated_at = models.DateTimeField(auto_now=True)
    
    
    class Meta:
        ordering = ['-issue_date']
    
    @property
    def primary_event(self):
        first = self.event_dates.first()
        return {
            "date": first.date,
            "location": first.date_location
        } if first else None

    @property
    def all_event_details(self):
        return list(self.event_dates.values("date", "date_location"))

    @property
    def total_amount(self):
        return sum(item.line_total for item in self.invoice_items.all())
    
    @property
    def total_payments_made(self):
        """
        Returns the sum of all COMPLETED payments for this invoice
        """
        # Filter only completed payments and sum their amounts
        result = self.payment_transaction.filter(
            status=Payment.PaymentStatus.COMPLETED
        ).aggregate(
            total_payments=Sum('amount_paid')
        )
        return result['total_payments'] or 0  # Return 0 if no payments exist
    




    def create_invoice_items_from_booking(self):
        """Creates invoice items from the booking's packages and addons."""
        # Create items for packages
        self.invoice_items.filter(
        item_type__in=[InvoiceItem.ItemType.PACKAGE, InvoiceItem.ItemType.ADDON]
        ).delete()
        for package in self.packages.all():
            InvoiceItem.objects.get_or_create(
                invoice=self,
                item_type=InvoiceItem.ItemType.PACKAGE,
                package=package,
                defaults={
                    'description': package.package_name,
                    'unit_price': package.price,
                    'quantity': 1,
                    'item_type': InvoiceItem.ItemType.PACKAGE,
                    'is_taxable': False,
                }
            )
        
        # Create items for addons
        for addon in self.Addons.all():
            InvoiceItem.objects.get_or_create(
                invoice=self,
                addon=addon,
                defaults={
                    'description': addon.name,
                    'unit_price': addon.price,
                    'quantity': addon.quantity,
                    'item_type': InvoiceItem.ItemType.ADDON,
                    'is_taxable': True,
                }
            )

    def save(self, *args, **kwargs):
     
        
        if not self.booking_code:
            today_str = timezone.now().strftime('%Y%m%d')
            prefix = f"CGWBK-{today_str}"

            # Find the latest booking code starting with today's date
            last_code = self.__class__.objects.filter(
                booking_code__startswith=prefix
            ).aggregate(Max('booking_code'))['booking_code__max']

            if last_code:
                # Extract and increment the numeric part
                last_number = int(last_code.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1

            self.booking_code = f"{prefix}-{new_number:04d}"
        if not self.invoice_number:
            self.invoice_number = f"CGINV-{self.booking_code[6:]}"
            print(self.invoice_number)

        


        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.booking_code} by {self.client.username}"
        
    
class BookingDate(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='event_dates')
    date = models.DateField()
    date_location = models.CharField(max_length=255, blank=True, null= True)

    def __str__(self):
        return f"{self.booking.client} - {self.date} @ {self.date_location}"
    
    @property
    def primary_date(self):
        """Returns the first event date for backward compatibility"""
        first_date = self.event_dates.first()
        return first_date.date if first_date else None
    
    @property
    def all_dates(self):
        """Returns all event dates as a list"""
        return list(self.event_dates.values_list('date', flat=True))
    
    @property
    def has_multiple_dates(self):
        """Check if booking has multiple dates"""
        return self.event_dates.count() > 1


class InvoiceItem(models.Model):
    class ItemType(models.TextChoices):
        PACKAGE = 'package', 'Package'
        ADDON = 'addon', 'Add-On'
        SERVICE = 'service', 'Additional Service'
        DISCOUNT = 'discount', 'Discount'
        OTHER = 'other', 'Other'

    invoice = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='invoice_items', null=True)
    item_type = models.CharField(max_length=20, choices=ItemType.choices, null=True, blank=True)
    description = models.CharField(max_length=200, blank=True)
    deliverables = models.TextField(blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_taxable = models.BooleanField(default=True)
    is_discount = models.BooleanField(default=False)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True, blank=True)
    addon = models.ForeignKey(AddOn, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-id']

    @property
    def line_total(self):
        if self.item_type == 'discount':
            return self.quantity * (-self.price)
        return self.quantity * self.price
         
    @property
    def invoice_number(self):
        return self.invoice.invoice_number if self.invoice else None

    def __str__(self):
        return f"{self.description} (x{self.quantity}) @ {self.price}"
    
    def save(self, *args, **kwargs):
        # Automatically set fields from package or addon if not set
        print(self.invoice.client)
        if self.package and not any([self.description,self.deliverables, self.price]):
            self.description = self.package.package_name
            self.deliverables = self.package.deliverables
            self.price = self.package.price
            self.item_type = self.ItemType.PACKAGE
            
        if self.addon and not any([self.description,self.deliverables, self.price]):
            self.description = self.addon.name
            self.deliverables = self.package.deliverables
            self.price = self.addon.price
            self.item_type = self.ItemType.ADDON
            
        super().save(*args, **kwargs)





class Payment(models.Model):
    class PaymentMethod(models.TextChoices):
        CASH = 'Cash', 'Cash'
        BANK_TRANSFER = 'Bank Transfer', 'Bank Transfer'
        

    class PaymentStatus(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        COMPLETED = 'Completed', 'Completed'
        FAILED = 'Failed', 'Failed'
        REFUNDED = 'Refunded', 'Refunded'

    invoice = models.ForeignKey(Booking,  on_delete=models.CASCADE, related_name='payment_transaction')
    amount_paid = models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(0.01)], null=True)
    payment_date = models.DateTimeField(default=timezone.now)
    payment_method = models.CharField(max_length=50,choices=PaymentMethod.choices,default=PaymentMethod.BANK_TRANSFER)
    status = models.CharField(max_length=50,choices=PaymentStatus.choices,default=PaymentStatus.PENDING)
    transaction_id = models.CharField(max_length=100,blank=True,help_text="Payment gateway reference or receipt number")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Receipt fields
    # balance = models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(0.01)])
    receipt_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    receipt_issued_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)


    @property
    def balance(self):
        return self.invoice.total_amount - self.invoice.total_payments_made

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            today_str = timezone.now().strftime('%Y%m%d')
            prefix = f"CGRCP-{today_str}"

            # Find the latest booking code starting with today's date
            last_code = self.__class__.objects.filter(
                receipt_number__startswith=prefix
            ).aggregate(Max('receipt_number'))['receipt_number__max']

            if last_code:
                # Extract and increment the numeric part
                last_number = int(last_code.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1

            self.receipt_number = f"{prefix}-{new_number:04d}"

            print(self.invoice.total_amount)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment #{self.id} - {self.amount_paid} ({self.status})"

    class Meta:
        ordering = ['-payment_date']
        verbose_name = 'Payment Transaction'
        verbose_name_plural = 'Payment Transactions'

@receiver(post_save, sender=Payment)
def update_invoice_on_payment(sender, instance, created, **kwargs):
    invoice = instance.invoice
    invoice.amount_due = instance.balance
    print(invoice.amount_due)
    # print(instance.balance)
    invoice.save()

    print(instance.invoice.amount_due)



    




    