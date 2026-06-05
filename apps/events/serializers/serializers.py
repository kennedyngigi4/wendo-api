from rest_framework import serializers
from apps.events.models.models import Event

class EventHomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "id", "slug", "title", "banner", "excerpt", "venue_name", "start_datetime", "end_datetime", "is_paid", "ticket_price", "is_live"
        ]




