import uuid
from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError

# Create your models here.

class ServiceCategory(models.Model):

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)

    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    icon = models.ImageField(upload_to="services/", null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.name)
    

class Service(models.Model):

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    icon = models.ImageField(upload_to="services/", null=True, blank=True)
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)


    class Meta:
        unique_together = ("name", "category")
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = f"{self.name}-{self.category.name}"
            self.slug = slugify(f"{base}-{uuid.uuid4().hex[:8]}")

        super().save(*args, **kwargs)


    def __str__(self):
        return str(self.name)



class CustomService(models.Model):
    
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, null=True)
    icon = models.ImageField(upload_to="services/")

    provider = models.ForeignKey("providers.Provider", on_delete=models.CASCADE, null=True, blank=True)
    professional = models.ForeignKey("professionals.Professional", on_delete=models.CASCADE, null=True, blank=True)

    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            base = f"{self.name}"
            self.slug = slugify(f"{base}-{uuid.uuid4().hex[:8]}")

        super().save(*args, **kwargs)

    class Meta:
        unique_together = ("name", "provider", "professional")

    def clean(self):
        if not self.professional and not self.provider:
            raise ValidationError("Professional or Provider must be submitted.")
        
        if self.professional and self.provider:
            raise ValidationError("Only professional or provider allowed not both.")

    def __str__(self):
        return f"{self.name}"



class Specialty(models.Model):

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)

    profession = models.ForeignKey("professionals.ProfessionalType", on_delete=models.SET_NULL, null=True)
    

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.profession.name}")

        super().save(*args, **kwargs)

    class Meta:
        ordering = ["name"]

        constraints = [
            models.UniqueConstraint(
                fields=["name", "profession"],
                name="unique_specialty_per_profession"
            ),
            models.UniqueConstraint(
                fields=["slug", "profession"],
                name="unique_specialty_slug_per_profession"
            )
        ]


    def __str__(self):
        return f"{self.name}"




class ServiceOffering(models.Model):
    
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)

    provider = models.ForeignKey("providers.Provider", on_delete=models.CASCADE, null=True, blank=True, related_name="provider_services")
    branch = models.ForeignKey("providers.ProviderBranch", on_delete=models.CASCADE, null=True, blank=True, related_name="branch_services")
    professional = models.ForeignKey("professionals.Professional", on_delete=models.CASCADE, null=True, blank=True, related_name="professional_services")
    
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="services_offerings")
    service_category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, null=True, related_name="service_categories")

    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("branch", "service", "professional")
        

    def __str__(self):
        return f"{self.service.name}"


