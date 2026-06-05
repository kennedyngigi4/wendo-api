import uuid
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from apps.accounts.models.models import User
from apps.providers.models.models import Provider


class EventCategory(models.TextChoices):
    HEALTH_TALK = "health_talk", "Health Talk"
    MEDICAL_CAMP = "medical_camp", "Medical Camp"
    WEBINAR = "webinar", "Webinar"
    SCREENING = "screening", "Health Screening"
    CONFERENCE = "conference", "Conference"
    WORKSHOP = "workshop", "Workshop"
    OTHER = "other", "Other"


class EventMode(models.TextChoices):
    ONLINE = "online", "Online"
    ONSITE = "onsite", "Onsite"
    HYBRID = "hybrid", "Hybrid"


class EventStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PENDING = "pending", "Pending"
    PUBLISHED = "published", "Published"
    CANCELLED = "cancelled", "Cancelled"
    COMPLETED = "completed", "Completed"


class Event(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Basic Info
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    excerpt = models.TextField(null=True)
    description = models.TextField()

    category = models.CharField(
        max_length=50,
        choices=EventCategory.choices,
        default=EventCategory.HEALTH_TALK
    )

    mode = models.CharField(
        max_length=20,
        choices=EventMode.choices,
        default=EventMode.ONSITE
    )

    status = models.CharField(
        max_length=20,
        choices=EventStatus.choices,
        default=EventStatus.DRAFT
    )

    # Organizers (flexible: doctor, hospital, company, NGO)
    organizer = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name="organized_events")

    # Timing
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    is_all_day = models.BooleanField(default=False)

    # Location (important for healthcare camps etc.)
    venue_name = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=120, blank=True, null=True)
    country = models.CharField(max_length=120, default="Kenya")

    # Online event support
    meeting_link = models.URLField(blank=True, null=True)

    # Capacity & registration
    max_attendees = models.PositiveIntegerField(blank=True, null=True)
    is_registration_required = models.BooleanField(default=True)
    registration_deadline = models.DateTimeField(blank=True, null=True)

    # Event media
    banner = models.ImageField(upload_to="events/banners/", blank=True, null=True)

    # Pricing (for paid workshops or conferences)
    is_paid = models.BooleanField(default=False)
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # SEO / discovery
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated tags")

    # Tracking
    is_featured = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_datetime"]

    def __str__(self):
        return self.title

    @property
    def is_upcoming(self):
        return self.start_datetime > timezone.now()

    @property
    def is_live(self):
        now = timezone.now()
        return self.start_datetime <= now <= self.end_datetime


    def save(self, *args, **kwargs):
        
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.category}")

        super().save(*args, **kwargs)
