from django.shortcuts import render, get_object_or_404
from django.db.models import Max, Avg, Value
from django.db.models.functions import Coalesce
from django.core.cache import cache

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView, View

from apps._core_utils.helpers.cache_utils import GlobalCache
from apps.professionals.models.models import *
from apps.professionals.serializers.public_serializers import *
from apps.accounts.models.models import *
from apps.accounts.permissions import IsProvider



class ProfessionalsHomeView(APIView):

    CACHE_PREFIX = "home_professionals"

    def get(self, request):

        cache_key = GlobalCache().get_list_public_key(self.CACHE_PREFIX)
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        queryset = Professional.objects.all()
        data = ProfessionalHomeSerializer(queryset, many=True).data

        cache.set(cache_key, data, timeout=60 * 10)

        return Response(data)
    

class AllProfessionalsView(APIView):

    CACHE_PREFIX = "all_professionals"

    def get(self, request):

        cache_key = GlobalCache().get_list_public_key(self.CACHE_PREFIX)
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)
   
        queryset = Professional.objects.select_related(
            "professional_type"
        ).prefetch_related(
            "specialties"
        ).annotate(
            avg_rating = Coalesce(Avg("reviews__rating"), Value(0.0))
        )

        data = ProfessionalCardSerializer(queryset, many=True, context={"request": request}).data
        cache.set(cache_key, data, timeout=60 * 10)

        return Response(data)
    


class ProfessionalDetailsView(generics.GenericAPIView):

    CACHE_PREFIX = "professional_data"
    serializer_class = ProfessionalDetailsSerializer

    def get(self, request, *args, **kwargs):
        slug = kwargs.get("slug")

        cache_key = GlobalCache().get_detail_public_key(prefix=self.CACHE_PREFIX, item_id=slug)
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)
        
        special = get_object_or_404(
            Professional.objects.select_related( 
                "professional_type"
            ).prefetch_related(
                "specialties", "professional_education", "operating_hours", 
                "professional_services", "reviews"
            ).annotate(
                avg_rating=Coalesce(Avg("reviews__rating"), Value(0.0))
            ),
            slug=slug,
            is_active=True
        )

        data = self.get_serializer(special).data
        cache.set(cache_key, data, timeout=60 * 10)

        return Response(data)


