import uuid
from django.db import models
from apps.accounts.models.models import *


class PatientProfile(models.Model):

    GENDER_CHOICES = [
        ( "female", "Female"),
        ( "male", "Male"),
    ]

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="patientprofile")

    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to="users/accounts", null=True, blank=True)

    country = models.CharField(max_length=20, null=True, blank=True)


    def __str__(self):
        return f"{self.user}"





class ProviderProfile(models.Model):

    GENDER_CHOICES = [
        ( "female", "Female"),
        ( "male", "Male"),
    ]

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="providerprofile")

    email_verified = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False)

    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to="users/accounts", null=True, blank=True)

    country = models.CharField(max_length=20, null=True, blank=True)


    def __str__(self):
        return f"{self.user}"



