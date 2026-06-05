from django.contrib import admin

from apps.bookings.models.models import Booking

# Register your models here.
# admin.site.register(Booking)
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "provider",
        "branch",
        "appointment_date",
        "status",
        "created_at",
    )

    search_fields = (
        "name",
        "email",
        "phone",
    )

    ordering = ("-created_at",)


