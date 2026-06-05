import uuid
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.text import slugify


from apps.accounts.models.models import User
from apps.providers.models.models import ProviderBranch, Provider
from apps.professionals.models.models import Professional
# Create your models here.


class Feature(models.Model):

    VALUE_TYPE_CHOICES = [
        ( "boolean", "Boolean"),
        ( "number", "Number"),
        ( "text", "Text"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    key = models.SlugField(max_length=100, unique=True)  # e.g max_branches
    name = models.CharField(max_length=255, help_text="Branches limit")              # e.g Branches Limit
    value_type = models.CharField(max_length=20, choices=VALUE_TYPE_CHOICES, default="text")


    def save(self, *args, **kwargs):

        if not self.key:
            base_key = slugify(self.name).replace("-", "_")

            key = base_key
            counter = 1
            while Feature.objects.filter(key=key).exists():
                key = f"{base_key}-{counter}"
                counter += 1
            self.key = key
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.name)


class Plan(models.Model):

    PLAN_FOR_CHOICES = [
        ("provider", "Provider"),
        ("professional", "Professional"),
        ("all", "All"),
    ]

    DURATION_CHOICES = [
        ( "month", "Month"),
        ( "quarterly", "Quarterly"),
        ( "semi_annually", "Semi Annually"),
        ( "annually", "Annually"),
        ( "bitrienary", "Bitrienary"),
        ( "tritrienary", "Tritrienary"),
    ]

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)

    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)

    plan_for = models.CharField(max_length=30, choices=PLAN_FOR_CHOICES, null=True)

    price = models.IntegerField(null=True, blank=True)
    discounted_price = models.IntegerField(null=True, blank=True)

    max_days = models.PositiveIntegerField()
    duration = models.CharField(max_length=30, choices=DURATION_CHOICES)

    features = models.ManyToManyField(Feature, through="PlanFeature", related_name="plans")

    is_free = models.BooleanField(default=False)
    is_trial = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{uuid.uuid4().hex[:6]}")
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name}"



class PlanFeature(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE)

    value = models.CharField(max_length=255, help_text="e.g true, 10, unlimited")  # store "true", "10", "unlimited"

    class Meta:
        unique_together = ("plan", "feature")

    def __str__(self):
        return f"{self.plan.name} - {self.feature.key}: {self.value}"



class Subscription(models.Model):

    STATUS_CHOICES = [
        ("active", "Active"),
        ("expired", "Expired"),
        ("cancelled", "Cancelled"),
        ("pending", "Pending"),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subscriptions", null=True)
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="subscriptions", null=True)

    branch = models.ForeignKey(ProviderBranch, on_delete=models.CASCADE, null=True, blank=True, related_name="subscriptions")
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE, null=True, blank=True, related_name="subscriptions")


    start_date = models.DateTimeField(auto_now_add=True, null=True)
    end_date = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="pending")
    is_active = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.plan.name}"




class Promotion(models.Model):

    PROMO_TYPE_CHOICES = [
        ("trial", "Trial"),
        ("discount", "Discount"),
        ("free_access", "Free Access"),
    ]

    APPLY_TO_CHOICES = [
        ("provider", "Provider"),
        ("professional", "Professional"),
        ("all", "All"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True, null=True, blank=True)

    promo_type = models.CharField(max_length=20, choices=PROMO_TYPE_CHOICES)
    apply_to = models.CharField(max_length=20, choices=APPLY_TO_CHOICES, default="all")

    free_days = models.PositiveIntegerField(null=True, blank=True)  # e.g 90
    discount_percent = models.PositiveIntegerField(null=True, blank=True)  # e.g 20

    is_first_time_only = models.BooleanField(default=False)


    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name






class PromotionRedemption(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, related_name="redemptions")
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)

    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True, blank=True)
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE, null=True, blank=True)

    redeemed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("promotion", "user")







#==========================================================================================
#     FEATURED SUBSCRIPTIONS
#==========================================================================================
class FeaturedSubscriptionManager(models.Manager):
    def active(self):
        now = timezone.now()
        return self.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        )
    

class FeaturedSubscription(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    branch = models.ForeignKey(ProviderBranch, on_delete=models.CASCADE, related_name="featured_subscriptions")
    
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="featured_subscriptions")
    
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    objects = FeaturedSubscriptionManager()

    def __str__(self):
        return f"{self.plan.name} | {self.branch} ({self.start_date.date()} → {self.end_date.date()})"

    def is_currently_active(self):
        now = timezone.now()
        return (
            self.is_active and
            self.start_date <= now <= self.end_date
        )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["branch"],
                condition=Q(is_active=True),
                name="unique_active_subscription_per_branch"
            )
        ]

        indexes = [
            models.Index(fields=["branch", "is_active"]),
            models.Index(fields=["start_date", "end_date"]),
        ]


    




