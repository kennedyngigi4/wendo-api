from django.shortcuts import get_object_or_404
from apps.providers.models.models import Provider

class ProviderRepository:

    @staticmethod
    def get_provider(provider_id, user):

        return (
            get_object_or_404(
                Provider,
                id=provider_id,
                owner=user
            )
        )


