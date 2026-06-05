import uuid
from django.db import models
from apps.accounts.models.models import *


class Organization(models.Model):


    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.name}"




