import uuid
from django.db import models
from django.core.exceptions import ValidationError

from apps.providers.models.models import ProviderBranch
from apps.professionals.models.models import Professional


# Create your models here.


class Review(models.Model):

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    provider_branch = models.ForeignKey(ProviderBranch, related_name="reviews", on_delete=models.CASCADE, null=True, blank=True)
    professional = models.ForeignKey(Professional, related_name="reviews", on_delete=models.CASCADE, null=True, blank=True)

    rating = models.IntegerField()
    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if not self.provider_branch and not self.professional:
            raise ValidationError("Review must belong to a provider or professional.")
        
        if self.provider_branch and self.professional:
            raise ValidationError("Review cannot belong to both.")


    def __str__(self):
        return f"{self.comment}"

