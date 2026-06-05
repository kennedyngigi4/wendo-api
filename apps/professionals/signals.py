from datetime import timedelta

from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone


from rest_framework.exceptions import ValidationError

from apps.professionals.models.models import Professional
from apps.professionals.services.professional_services import ProfessionalsServices
from apps.subscriptions.models.models import Plan, Subscription



@receiver(post_save, sender=Professional)
def create_professional_trial_subscription(sender, created, instance, **kwargs):

    if created and instance.user:
        ProfessionalsServices.create_trial_subscription(instance)