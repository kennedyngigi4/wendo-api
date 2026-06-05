from django.utils import timezone
from apps.subscriptions.models.models import Subscription


def get_active_subscription_for_provider(provider):
    now = timezone.now()

    return Subscription.objects.filter(
        provider=provider,
        is_active=True,
        status="active",
        end_date__gte=now,
    ).order_by("-end_date").first()


