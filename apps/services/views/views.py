from django.shortcuts import render, get_object_or_404
from django.core.cache import cache

from rest_framework import status, generics,viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from apps._core_utils.helpers.cache_utils import GlobalCache
from apps.providers.models.models import Provider, ProviderBranch
from apps.professionals.models.models import Professional
from apps.accounts.permissions import IsProvider
from apps.services.models.models import ServiceCategory, Service, CustomService, Specialty, ServiceOffering
from apps.services.serializers.serializers import ServiceCategoryReadSearializer, ServiceOfferingWriteSerializer, ServiceOfferingReadSerializer, ServiceReadSearializer, CustomServiceReadSearializer, SpecialtyReadSerializer


# Create your views here.

class AllServicesView(APIView):
    def get(self, request):
        queryset = Service.objects.all().order_by("name")
        serializer = ServiceReadSearializer(queryset, many=True)
        return Response(serializer.data)



class AllSpecialtiesView(APIView):
    def get(self, request):

        cache_key = GlobalCache.get_list_public_key("specialties")
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        queryset = Specialty.objects.all().order_by("name")
        serializer = SpecialtyReadSerializer(queryset, many=True)

        cache.set(cache_key, serializer.data, GlobalCache.DEFAULT_TIMEOUT)

        return Response(serializer.data)




class ServiceOfferingViewset(viewsets.ViewSet):

    permission_classes = [IsAuthenticated, IsProvider]


    def get_queryset(self):
        user = self.request.user
        owner = self.request.query_params.get("owner_type")

        queryset = ServiceOffering.objects.all()

        if owner == "branch":
            branch_id = self.request.query_params.get("branch_id")
            if not branch_id:
                raise ValidationError("Branch id is required.")
            return queryset.filter(branch__id=branch_id, branch__provider__owner=user)

        elif owner == "provider":
            provider_id = self.request.query_params.get("provider_id")
            if not provider_id:
                raise ValidationError("Provider id is required.")
            return queryset.filter(provider__id=provider_id, provider__owner=user)

        elif owner == "professional":
            professional_id = self.request.query_params.get("professional_id")
            if not professional_id:
                raise ValidationError("Branch id is required.")
            return queryset.filter(professional__id=professional_id, professional__user=user)

        raise ValidationError("Invalid or missing context")
    

    def create(self, request):
        user = request.user
        owner = request.query_params.get("owner_type")

        data = request.data.copy()

        if owner == "branch":
            branch_id = request.query_params.get("branch_id")
            if not branch_id:
                raise ValidationError("Branch id is required.")

            branch = get_object_or_404(
                ProviderBranch,
                id=branch_id,
                provider__owner=user
            )
            data["branch"] = branch.id
            data["provider"] = branch.provider.id  # optional but consistent

        elif owner == "provider":
            provider_id = request.query_params.get("provider_id")
            if not provider_id:
                raise ValidationError("Provider id is required.")

            provider = get_object_or_404(
                Provider,
                id=provider_id,
                owner=user
            )
            data["provider"] = provider.id

        elif owner == "professional":
            professional_id = request.query_params.get("professional_id")
            if not professional_id:
                raise ValidationError("Professional id is required.")

            professional = get_object_or_404(
                Professional,
                id=professional_id,
                user=user
            )
            data["professional"] = professional.id

        else:
            raise ValidationError("Invalid or missing context")

        serializer = ServiceOfferingWriteSerializer(data=data)

        if serializer.is_valid():
            service = serializer.save()
            return Response({"success": True,  "message": "Service created successfully.",  "id": service.id }, status=status.HTTP_201_CREATED)

        return Response({ "success": False, "errors": serializer.errors }, status=status.HTTP_400_BAD_REQUEST)


    def list(self, request):
        queryset = self.get_queryset()
        serializer = ServiceOfferingReadSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        service_offering = get_object_or_404(queryset, id=pk)

        serializer = ServiceOfferingReadSerializer(service_offering)
        return Response(serializer.data)


    def partial_update(self, request, pk=None):
        queryset = self.get_queryset()
        service_offering = get_object_or_404(queryset, id=pk)

        serializer = ServiceOfferingWriteSerializer(service_offering, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "success": True,
            "message": "Service updated successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


    def destroy(self, request, pk=None):
        queryset = self.get_queryset()
        service_offering = get_object_or_404(queryset, id=pk)

        service_offering.delete()

        return Response({
            "success": True,
            "message": "Service deleted successfully.",
        }, status=status.HTTP_204_NO_CONTENT)




