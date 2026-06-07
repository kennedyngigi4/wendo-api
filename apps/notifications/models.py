import uuid
from django.db import models

from apps.accounts.models.models import User

# Create your models here.
class Notification(models.Model):

    NOTIFICATION_TYPES = [
        ( "educative", "Educative"),
        ( "general", "General"),
        ( "marketing", "Marketing"),
        ( "personal", "Personal"),
    ]

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=255)
    message = models.TextField()

    type = models.CharField(max_length=40, choices=NOTIFICATION_TYPES)

    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(auto_now=True)

    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.user.fullname} - {self.title}"



class NewsletterSubscriber(models.Model):
    
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    email = models.EmailField(unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email}"

