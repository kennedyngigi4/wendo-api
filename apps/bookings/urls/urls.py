from django.urls import path
from apps.bookings.views.views import PatientBookingsViewset, ProviderProfessionalBookingsViewset
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"patient_bookings", PatientBookingsViewset, basename="patient_bookings")
router.register(r"provprof_bookings", ProviderProfessionalBookingsViewset, basename="provprof_bookings")
urlpatterns = router.urls
