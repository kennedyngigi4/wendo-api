import uuid
from django.db import models
from django.utils.text import slugify
from tinymce.models import HTMLField

from apps.accounts.models.models import User
from apps.accounts.models.organization_models import *
from apps.services.models.models import Service

# Create your models here.


class Provider(models.Model):
    PROVIDER_TYPES = [
        ( "ambulance", "Ambulance"),
        ( "clinic", "Clinic"),
        ( "hospital", "Hospital"),
        ( "lab", "Laboratory"),
        ( "pharmacy", "Pharmacy"),
    ]

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    provider_type = models.CharField(max_length=30, choices=PROVIDER_TYPES)

    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    country = models.CharField(max_length=20)

    logo = models.ImageField(upload_to="", blank=True, null=True)
    banner = models.ImageField(upload_to="", blank=True, null=True)

    description = HTMLField()

    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.provider_type}-{uuid.uuid4().hex[:6]}")
        
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.name} - (active: {self.is_active})"


class ProviderBranch(models.Model):

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name="branches")

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    phone = models.CharField(max_length=20)
    whatsapp_phone = models.CharField(max_length=20, null=True, blank=True)
    emergency_phone = models.CharField(max_length=20, null=True, blank=True)

    email = models.EmailField(blank=True)

    location_name = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=15, decimal_places=12, null=True, blank=True)
    longitude = models.DecimalField(max_digits=15, decimal_places=12, null=True, blank=True)
    country = models.CharField(max_length=20, null=True, blank=True)

    banner = models.ImageField(upload_to="", blank=True)

    is_main_branch = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)

    is_featured_manual = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.provider.provider_type}-{uuid.uuid4().hex[:6]}")
        
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.name} - (active: {self.is_active})"



class OperatingHours(models.Model):

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)

    branch = models.ForeignKey(ProviderBranch, on_delete=models.CASCADE, related_name="operating_hours")

    day_of_week = models.IntegerField()
    open_time = models.TimeField(null=True, blank=True)
    close_time = models.TimeField(null=True, blank=True)

    is_24 = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.branch.name} - {self.day_of_week} - ({self.open_time} - {self.close_time})"




