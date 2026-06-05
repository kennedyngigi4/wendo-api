import uuid
from django.db import models
from django.utils.text import slugify
from tinymce.models import HTMLField

from apps.accounts.models.models import User
from apps.providers.models.models import ProviderBranch
from apps.services.models.models import Specialty
# Create your models here.

def professional_profile_upload_path(instance, filename):
    ext = filename.split('.')[-1] 
    prof_id = str(instance.id).replace("-", "")
    return f"professionals/profile/{prof_id}.{ext}"


class ProfessionalType(models.Model):

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    icon = models.ImageField(upload_to="professionals/", null=True, blank=True)

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(f"{self.name}")

        super().save(*args, **kwargs)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}"


class Professional(models.Model):

    GENDER_TYPES = [
        ( "female", "Female"),
        ( "male", "Male"),
        ( "not_say", "Choose not to say"),
    ]

    TITLE_CHOICES = [
        ("dr", "Doctor"),
        ("prof", "Professor"),
        ("mr", "Mr"),
        ("mrs", "Mrs"),
        ("miss", "Miss"),
    ]


    CONSULTATION_TYPES = [
        ("in_person", "In-person Consultation"),
        ("virtual", "Virtual Consultation"),
        ("home_visit", "Home Visit"),
        ("emergency", "Emergency Consultation"),
        ("follow_up", "Follow-up Consultation"),
    ]

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    slug = models.SlugField(max_length=255, unique=True, null=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name="professional_profile")


    name = models.CharField(max_length=255)
    title = models.CharField(max_length=10, choices=TITLE_CHOICES, default="dr")

    license_number = models.CharField(max_length=100, blank=True)
    bio = HTMLField()
    professional_type = models.ForeignKey(ProfessionalType, on_delete=models.CASCADE, null=True)
    specialties = models.ManyToManyField(Specialty)
    years_of_experience = models.IntegerField(default=0)
    consultation_fee = models.IntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_TYPES)

    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)

    profile_photo = models.ImageField(upload_to=professional_profile_upload_path)

    
    location_name = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.DecimalField(max_digits=12, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=12, decimal_places=8, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)

    consultation_types = models.JSONField(default=list, blank=True)
    introduction_video_url = models.TextField(null=True, blank=True)

    accepts_nhif = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_featured_manual = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)


    def save(self, *args, **kwargs):
        
        if not self.slug:
            base_slug = f"{self.name}-{self.professional_type.name}"
            suffix_slug = uuid.uuid4().hex[:10]

            self.slug = slugify(f"{base_slug}-{suffix_slug}")
        
        super().save(*args, **kwargs)
    

    def __str__(self):
        return f"{self.name}"


class Education(models.Model):

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)

    professional = models.ForeignKey(Professional, on_delete=models.CASCADE, related_name="professional_education")

    degree = models.CharField(max_length=255)  # e.g. MBChB, MPH
    institution = models.CharField(max_length=255)  # e.g. University of Nairobi
    year_completed = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.degree} - {self.institution}"


class OperatingHours(models.Model):

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)

    professional = models.ForeignKey(Professional, on_delete=models.CASCADE, related_name="operating_hours")

    day_of_week = models.IntegerField()
    open_time = models.TimeField(null=True, blank=True)
    close_time = models.TimeField(null=True, blank=True)

    is_24 = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.professional.name} - {self.day_of_week} - ({self.open_time} - {self.close_time})"




class ProfessionalBranch(models.Model):

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)

    professional = models.ForeignKey(Professional, on_delete=models.CASCADE)
    branch = models.ForeignKey(ProviderBranch, on_delete=models.CASCADE)

    specialty = models.ForeignKey(Specialty, on_delete=models.SET_NULL, null=True)

    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)


    def __str__(self):
        return f"{self.professional.name}"


