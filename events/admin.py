from django.contrib import admin
from .models import Package, Booking, Payment, AddOn, InvoiceItem, BookingDate



class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_code', 'client', 'wedding_date', 'total_amount_display','total_payments_made_display','amount_due_display')
    readonly_fields = ('total_amount_display','total_payments_made_display')

    ordering = ('-created_at',)  # sort by newest first
    
    def amount_due_display(self, obj):
        return f"₦{obj.total_amount - obj.total_payments_made }"
    amount_due_display.short_description = 'Amount Due'

    def total_payments_made_display(self, obj):
        return f"₦{obj.total_payments_made:,.2f}"
    total_payments_made_display.short_description = 'Total Payments'

    def total_amount_display(self, obj):
        return f"₦{obj.total_amount:,.2f}"
    total_amount_display.short_description = 'Total Amount'





    
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ('invoice_number_display','user_display','__str__','item_type','quantity','price')
    readonly_fields = ('invoice_number_display',)

    def invoice_number_display(self, obj):
        return obj.invoice_number
    invoice_number_display.short_description = 'Invoice number'
    def user_display(self, obj):
        return obj.invoice.client
    user_display.short_description = 'client name'

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('invoice','__str__','status', 'amount_paid_display')
    # readonly_fields = ('balance_display',)

    # def balance_display(self, obj):
    #     return f"₦{obj.balance:,.2f}"
    # balance_display.short_description = 'Balance'

    def amount_paid_display(self, obj):
        return f"₦{obj.amount_paid:,.2f}"
    amount_paid_display.short_description = 'Amount Paid'


    def save(*args, **kwargs):
        super.save(*args, **kwargs)

    

admin.site.register(Booking, BookingAdmin)
# Register your models here.

admin.site.register(Package)
admin.site.register(AddOn)
admin.site.register(InvoiceItem, InvoiceItemAdmin )
admin.site.register(Payment, PaymentAdmin)
admin.site.register(BookingDate)
