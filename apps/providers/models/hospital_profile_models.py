import uuid
from django.db import models
from django.utils.text import slugify
from django.contrib.postgres.fields import ArrayField
from tinymce.models import HTMLField

from rest_framework.exceptions import ValidationError

from apps.accounts.models.models import User
from apps.providers.models.models import Provider, ProviderBranch
from apps.services.models.models import Specialty



class HospitalProfile(models.Model):

    OWNERSHIP_TYPE = [
        ("public", "Public"),
        ("private", "Private"),
        ("mission", "Mission/Faith-based"),
        ("ngo", "NGO"),
    ]

    LEVEL = [
        ("level_2", "Level 2"),
        ("level_3", "Level 3"),
        ("level_4", "Level 4"),
        ("level_5", "Level 5"),
        ("level_6", "Level 6"),
    ]


    TRUST_REASON_CHOICES = [
        ("friendly_staff", "Friendly & Caring Staff"),
        ("short_waiting_time", "Short Waiting Time"),
        ("affordable_services", "Affordable Healthcare Services"),
        ("insurance_accepted", "Insurance Accepted"),
        ("experienced_doctors", "Experienced Doctors"),
        ("clean_environment", "Clean & Comfortable Environment"),
        ("quality_patient_care", "Quality Patient Care"),
        ("fast_service", "Fast & Efficient Service"),
        ("modern_equipment", "Modern Medical Equipment"),
        ("privacy_confidentiality", "Patient Privacy & Confidentiality"),
        ("open_weekends", "Open on Weekends"),
        ("24_7_services", "24/7 Medical Services"),
        ("laboratory_services", "Laboratory Services Available"),
        ("pharmacy_available", "On-Site Pharmacy Available"),
        ("specialist_consultations", "Specialist Consultations Available"),
    ]


    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)

    branch = models.OneToOneField(ProviderBranch, on_delete=models.CASCADE, related_name="hospital_profile")

    ownership_type = models.CharField(max_length=20, choices=OWNERSHIP_TYPE, blank=True)
    level = models.CharField(max_length=10, choices=LEVEL, blank=True)
    accepts_nhif = models.BooleanField(default=False)
    year_established = models.IntegerField(null=True, blank=True)
    has_pharmacy = models.BooleanField(default=False)

    total_beds = models.IntegerField(default=0)
    icu_beds = models.IntegerField(default=0)

    has_emergency = models.BooleanField(default=False)
    has_ambulance = models.BooleanField(default=False)

    trust_reasons = ArrayField(models.CharField(max_length=100), default=list, blank=True )

    facebook = models.URLField(max_length=500, null=True, blank=True)
    tiktok = models.URLField(max_length=500, null=True, blank=True)
    instagram = models.URLField(max_length=500, null=True, blank=True)
    linkedin = models.URLField(max_length=500, null=True, blank=True)
    youtube = models.URLField(max_length=500, null=True, blank=True)
    twitter_x = models.URLField(max_length=500, null=True, blank=True)


    def __str__(self):
        return f"{self.branch.name}"



class WardType(models.Model):

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    name = models.CharField(max_length=100) #e.g General Ward, Private Ward, ICU, Maternity, Pediatric

    def __str__(self):
        return f"{self.name}"
    

class HospitalWard(models.Model):

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)

    branch = models.ForeignKey(ProviderBranch, on_delete=models.CASCADE, null=True, related_name="hospital_wards")
    ward_type = models.ForeignKey(WardType, on_delete=models.CASCADE, related_name="wards_type")

    total_beds = models.IntegerField(default=0)
    available_beds = models.IntegerField(default=0)

    is_active = models.BooleanField(default=False)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)


    def __str__(self):
        return f"{self.branch.name} - {self.ward_type}"
    


class Specialist(models.Model):

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)

    title = models.CharField(max_length=25)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    photo = models.ImageField(upload_to="")
    specialties = models.ManyToManyField(Specialty)
    bio = HTMLField()
    branch = models.ForeignKey(ProviderBranch, on_delete=models.CASCADE, null=True)

    profession = models.ForeignKey("professionals.ProfessionalType", on_delete=models.CASCADE, null=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{uuid.uuid4().hex[:8]}")
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.title}"





class ClinicSession(models.Model):

    class WeekDay(models.IntegerChoices):
        MONDAY = 1, "Monday"
        TUESDAY = 2, "Tuesday"
        WEDNESDAY = 3, "Wednesday"
        THURSDAY = 4, "Thursday"
        FRIDAY = 5, "Friday"
        SATURDAY = 6, "Saturday"
        SUNDAY = 7, "Sunday"

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    branch = models.ForeignKey(ProviderBranch, on_delete=models.CASCADE, related_name="clinic_sessions")

    consultation_fee = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    banner = models.ImageField(upload_to="", null=True)
    description = HTMLField(null=True)

    specialists = models.ManyToManyField(Specialist, blank=True)

    days_of_week = models.JSONField(default=list, blank=True)

    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    max_patients = models.PositiveIntegerField(default=0)
    slot_duration = models.PositiveIntegerField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.branch_id}-{uuid.uuid4().hex[:6]}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.branch}"


