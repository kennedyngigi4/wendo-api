import uuid
from django.db import models
from django.utils import timezone

from apps.accounts.models.models import User
from apps.professionals.models.models import *
from apps.providers.models.models import *

# Create your models here.

class Booking(models.Model):

    STATUS = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="user_bookings")
    

    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True, blank=True, related_name="provider_bookings")
    branch = models.ForeignKey(ProviderBranch, null=True, blank=True, on_delete=models.SET_NULL, related_name="branch_bookings")
    professional = models.ForeignKey(Professional, null=True, blank=True, on_delete=models.SET_NULL, related_name="professional_bookings")

    name = models.CharField(max_length=255, null=True)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=20, null=True)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.TextField(blank=True)
    service = models.ForeignKey(ServiceOffering, on_delete=models.PROTECT, null=True)

    status = models.CharField(max_length=20, choices=STATUS, default="pending")
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return f"Booking by {self.name} - at ({self.appointment_date} : {self.appointment_time})"
