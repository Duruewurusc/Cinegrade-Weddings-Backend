from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('package', views.PackageViewSet)
router.register('users', views.UserViewSet)
router.register('bookings', views.BookingViewSet)
router.register('payments', views.PaymentViewSet)
router.register('gallery', views.GalleryViewSet)
router.register('addon', views.AddOnViewSet)
router.register('companyinfo', views.CompanyInfoViewSet)
router.register('invoiceitem', views.InvoiceItemViewSet)
router.register('testimonials', views.TestimonialViewSet)

urlpatterns = [
    path('', include(router.urls)),
]