from django.shortcuts import render, get_object_or_404
from django.core.cache import cache
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.response import Response

from apps._core_utils.services.search_services import SearchService
from apps.blogs.models import Blog
from apps.blogs.services.services import BlogService
from apps.professionals.models.models import Professional
from apps.providers.models.models import Provider, ProviderBranch
from apps.providers.services.providers_services import ProvidersService
from apps.professionals.services.professional_services import ProfessionalsServices
from apps.events.services.events_services import EventsService


class MainHomeView(APIView):

    def get(self, request):

        cache_key = "homepage_featured"
        cached = cache.get(cache_key)

        if cached is not None:
            return Response(cached)
        
        data = {
            "providers": ProvidersService.featured_providers(request),
            "professionals": ProfessionalsServices.featured_professionals(request),
            "blogs": BlogService.home_blogs(request),
            "events": EventsService.home_events(request)
        }

        cache.set(cache_key, data, timeout=60)
        return Response(data)



class GlobalSearchView(APIView):

    def get(self, request):

        query = request.query_params.get("q", "").strip()

        if not query:
            return Response({
                "query": "",
                "specialists": [],
                "branches": [],
                "blogs": []
            })
        

        cache_key = f"global_search_{query.lower()}"
        cached = cache.get(cache_key)

        if cached:
            return Response(cached)

        print(SearchService().search_specialists(query, request))

        response_data = {
            "query": query,
            "specialists": SearchService().search_specialists(query, request),
            "branches": SearchService().search_branches(query, request),
            # "blogs": SearchService().search_blogs(query)
        }

       

        cache.set(cache_key, response_data, timeout=60)

        return Response(response_data)

