from rest_framework.permissions import BasePermission
from django.utils import timezone
from apps.subscriptions.models.models import Subscription



class HasActiveProviderSubscription(BasePermission):
    message = "Subscription expired. Please renew to continue."


    def has_permission(self, request, view):
        provider_id = request.data.get("provider") or request.query_params.get("provider")
        
        if not provider_id:
            return True 
        
        now = timezone.now()

        return Subscription.objects.filter(
            provider_id=provider_id,
            is_active=True,
            status="active",
            end_date__gte=now,
        ).exists()


