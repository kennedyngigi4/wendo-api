from django.dispatch import receiver
from django.db.models.signals import post_save


from apps.providers.models.models import ProviderBranch
from apps.subscriptions.models.models import Subscription
from apps.providers.services.providers_services import ProvidersService


@receiver(post_save, sender=ProviderBranch)
def create_branch_trial_subscription(sender, instance, created, **kwargs):

    if created and instance.provider.owner:
        ProvidersService.create_branch_trial_subscription(instance)
    


