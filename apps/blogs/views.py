from django.shortcuts import render
from django.core.cache import cache

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from apps._core_utils.helpers.cache_utils import GlobalCache
from apps.blogs.models import Blog, BlogCategory
from apps.blogs.serializers import BlogCategorySerializer, BlogHomeSerializer

# Create your views here.


class AllBlogsView(APIView):

    def get(self, request):

        cache_key = GlobalCache().get_list_public_key("wendo_blogs")
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        queryset = Blog.objects.all().order_by("-published_at")
        data = BlogHomeSerializer(queryset, many=True, context={"request": request}).data


        cache.set(cache_key, data, timeout=GlobalCache().DEFAULT_TIMEOUT)

        return Response(data)



