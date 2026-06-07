from django.shortcuts import render
from django.core.cache import cache

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.events.services.events_services import EventsService


# Create your views here.

class AllUpcomingEvents(APIView):

    def get(self, request):

        cache_key = "all_events"
        cached = cache.get(cache_key)

        if cached is not None:
            return Response(cached)

        data = {
            "events": EventsService.all_events(request)
        }


        cache.set(cache_key, data, timeout=60)
        return Response(data)


