from django.utils import timezone
from apps.events.models.models import Event
from apps.events.serializers.serializers import EventHomeSerializer

class EventsService:

    @staticmethod
    def home_events(request):
        queryset = Event.objects.filter(
            start_datetime__gte=timezone.now()
        ).order_by(
            "start_datetime"
        )[:4]

        serializer = EventHomeSerializer(queryset, many=True, context={"request": request})
        return serializer.data



    @staticmethod
    def all_events(request):
        queryset = Event.objects.filter(
            end_datetime__gte=timezone.now()
        ).order_by(
            "start_datetime"
        )


        serializer = EventHomeSerializer(queryset, many=True, context={"request": request})
        return serializer.data
