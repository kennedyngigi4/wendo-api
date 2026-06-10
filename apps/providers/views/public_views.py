from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db.models import FloatField, IntegerField, Prefetch, Q, Max, Avg, Count, Value
from django.db.models.functions import Coalesce
from django.core.cache import cache

from rest_framework import generics, views, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from apps.providers.models.models import *
from apps.providers.serializers.public_serializers import *
from apps.subscriptions.models.models import FeaturedSubscription



class MainPagination(PageNumberPagination):
    page_size = 20


class AllProvidersViewSet(generics.ListAPIView):
    serializer_class = ProviderBranchCardSerializer
    pagination_class = MainPagination

    PROVIDER_TYPE_MAP = {
        "hospitals": "hospital",
        "clinics": "clinic",
        "pharmacies": "pharmacy",
        "laboratories": "laboratory",
    }

    def get_queryset(self):
        today = timezone.localtime(timezone.now()).weekday()

        queryset = (
            ProviderBranch.objects.filter(
                is_active=True,
                provider__is_active=True
            )
            .select_related(
                "provider",
                "hospital_profile"
            )
            .prefetch_related(
                Prefetch(
                    "operating_hours",
                    queryset=OperatingHours.objects.filter(day_of_week=today)
                ),
            )
            .annotate(
                avg_rating=Coalesce(
                    Avg("reviews__rating"),
                    Value(0.0),
                    output_field=FloatField()
                ),
                total_reviews=Coalesce(
                    Count("reviews"),
                    Value(0),
                    output_field=IntegerField()
                )
            )
        )

        # Route-based provider type
        page_type = self.kwargs.get("provider_page")
        provider_type = self.PROVIDER_TYPE_MAP.get(page_type)

        if provider_type:
            queryset = queryset.filter(
                provider__provider_type=provider_type
            )

        # Dynamic filters
        location = self.request.query_params.get("location")
        level = self.request.query_params.get("level")
        services = self.request.query_params.get("services")

        if location:
            queryset = queryset.filter(
                location__icontains=location
            )

        if level:
            queryset = queryset.filter(
                hospital_profile__level=level
            )

        if services:
            queryset = queryset.filter(
                services__name__icontains=services
            ).distinct()

        return queryset

    def list(self, request, *args, **kwargs):
        today = timezone.localtime(timezone.now()).weekday()

        page_number = request.query_params.get("page", 1)
        page_type = kwargs.get("provider_page", "")

        location = request.query_params.get("location", "")
        level = request.query_params.get("level", "")
        services = request.query_params.get("services", "")

        cache_key = (
            f"{page_type}_page_{page_number}_"
            f"day_{today}_"
            f"loc_{location}_"
            f"lvl_{level}_"
            f"srv_{services}"
        )
        

        # cached_data = cache.get(cache_key)
        
        # if cached_data:
        #     return Response(cached_data)

        queryset = self.filter_queryset(
            self.get_queryset()
        )

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)

            response = self.get_paginated_response(
                serializer.data
            )

            # cache.set(cache_key, response.data, timeout=60 * 1)

            return response

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context



class ProviderDetailsView(generics.GenericAPIView):
    serializer_class = ProviderBranchDetailsSerializer

    def get(self, request, *args, **kwargs):
        slug = kwargs.get("slug")

        queryset = get_object_or_404(
            ProviderBranch.objects.select_related(
                "provider"
            ).prefetch_related(
                "operating_hours", "branch_services", "hospital_profile", "hospital_wards", "clinic_sessions", "reviews"
            ).annotate(
                avg_rating=Coalesce(Avg("reviews__rating"), Value(0.0)),
                total_reviews=Coalesce(Count("reviews"), Value(0))
            ),
            is_active=True,
            slug=slug,
            provider__is_active=True
        )

        serializer = self.get_serializer(queryset)
        return Response(serializer.data)

