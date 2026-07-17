from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Max, Min, Q
from django.core.cache import cache

from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from apps._core_utils.helpers.cache_utils import GlobalCache
from apps.accounts.models.models import User
from apps.accounts.permissions import IsProvider
from apps.providers.models.models import *
from apps.providers.models.hospital_profile_models import *
from apps.professionals.models.models import Professional
from apps.providers.serializers.serializers import *
from apps.bookings.models.models import Booking
from apps.providers.serializers.serializers import *

from apps.providers.services.providers_services import ProvidersService
from apps.providers.services.branch_service import BranchService

from apps.subscriptions.services.services import *
from apps.providers.serializers.hospital_serializers import HospitalProfileReadSerializer, HospitalProfileWriteSerializer

#===================================================================
#       PROVIDER OVERVIEW MODE VIEWS
#===================================================================
class MyWorkspaceView(APIView):
    permission_classes = [IsAuthenticated, IsProvider]

    def get(self, request):
        user = self.request.user

        professional = Professional.objects.filter(user=user).first()
        organizations = ProviderBranch.objects.filter(
            provider__owner=user
        ).only("id", "name")

        professional_data = None
        if professional:
            professional_data =  ProfessionalDashboardSerializer(professional).data
            professional_data["type"] = "professional"
        
        organizations_data = ProviderDashboardSerializer(organizations, many=True).data
        for org in organizations_data:
            org["type"] = "provider"

        return Response({
            "professional": professional_data,
            "organizations": organizations_data
        })


class DashboardView(APIView):
    permission_classes = [IsAuthenticated, IsProvider]

    def get(self, request):
        user = self.request.user

        response = {
            "stats": ProvidersService.get_provider_stats(user),
            "companies": ProvidersService.get_provider_companies(user, request),
            "branches": ProvidersService.get_provider_branches(user),
            "professional": ProvidersService.get_provider_professional(user, request),
            "subscriptions": ProvidersService.get_provider_subscriptions(user),
        }


        return Response(response)


class OrganizationsView(viewsets.ViewSet):

    permission_classes = [IsAuthenticated, IsProvider]

    def create(self, request):
        user = self.request.user
        serializer = ProviderOwnerWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        organization = serializer.save(owner=user)

        # Apply trial subscription after provider creation
        SubscriptionService.apply_trial_subscription(user=user, provider=organization)

        return Response({ "success": True, "message": "Organization/ company created.", "id": organization.id}, status=status.HTTP_201_CREATED)


    def list(self, request):
        user = self.request.user
        queryset = Provider.objects.filter(owner=user).annotate(
            total_branches=Count("branches")
        )
        serializer = ProviderOwnerListSerializer(queryset, many=True, context={"request": request})

        return Response(serializer.data)


    def retrieve(self, request, pk=None):
        pass

    def partial_update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        pass





class SubscriptionsView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsProvider]



    def create(self, request):
        pass


    def list(self, request):
        user = self.request.user
        
        response = ProvidersService.get_all_subscriptions(user)

        return Response(response)


    def retrieve(self, request, pk=None):
        pass
    


#===================================================================
#       PROVIDER BRANCH TYPE VIEWS
#===================================================================

class BranchDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsProvider]

    def get(self, request):
        user = request.user
        branch_id = self.request.query_params.get("branch_id")

        branch = ProviderBranch.objects.get(id=branch_id)

        data = {
            "stats": ProvidersService.get_stats(branch),
            "bookings_trend": ProvidersService.get_bookings_trend(branch),
            "bookings_by_service": ProvidersService.get_bookings_by_service(branch),
            "recent_bookings": ProvidersService.get_recent_bookings(branch),
            "top_services": ProvidersService.get_top_services(branch),
            "latest_reviews": ProvidersService.get_latest_reviews(branch),
            "subscription": ProvidersService.get_latest_subscription(branch),
        }

        return Response(data)


class SpecialistsViewset(viewsets.ViewSet):

    permission_classes = [ IsAuthenticated, IsProvider ]

    def get_queryset(self):
        user = self.request.user
        owner = self.request.query_params.get("owner_type")

        queryset = Specialist.objects.all()

        if owner == "branch":
            branch_id = self.request.query_params.get("branch_id")
            if not branch_id:
                raise ValidationError("Branch id is required.")
            return queryset.filter(branch__id=branch_id, branch__provider__owner=user)
        
        elif owner == "provider":
            provider_id = self.request.query_params.get("provider_id")
            if not provider_id:
                raise ValidationError("Provider id is required.")
            return queryset.filter(branch__provider__id=provider_id, branch__provider__owner=user)
        raise ValidationError("Invalid or missing context")


    def create(self, request):
        serializer = SpecialistWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "success": True,
            "message": "Specialist listed successfully."
        }, status=status.HTTP_201_CREATED)
    

    def list(self, request):
        queryset = self.get_queryset()
        serializer = SpecialistReadCardSerializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        specialist = get_object_or_404(queryset, id=pk)

        serializer = SpecialistReadDetailsSerializer(specialist, context={"request": request})
        return Response(serializer.data)
    

    def partial_update(self, request, pk=None):
        queryset = self.get_queryset()
        specialist = get_object_or_404(queryset, id=pk)

        serializer = SpecialistWriteSerializer(
            specialist,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "success": True,
            "message": "Specialist updated successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    

    def destroy(self, request, pk=None):
        queryset = self.get_queryset()
        specialist = get_object_or_404(queryset, id=pk)

        specialist.delete()

        return Response({
            "success": True,
            "message": "Specialist deleted successfully.",
        }, status=status.HTTP_204_NO_CONTENT)


class ClinicSessionsViewset(viewsets.ViewSet):

    permission_classes = [IsAuthenticated, IsProvider]

    def get_queryset(self):
        user = self.request.user

        queryset = ClinicSession.objects.all()

        branch_id = self.request.query_params.get("branch_id")

        if not branch_id:
            raise ValidationError("Branch id is required.")
        
        return queryset.filter(branch__id=branch_id, branch__provider__owner=user)


    def create(self, request):
        serializer = ClinicSessionWriteSerializer(data=request.data)
        if serializer.is_valid():
            clinic_session = serializer.save()

            return Response({ 
                "success": True,
                "message": "Clinic session created successfully",
                "id": clinic_session.id,
            }, status=status.HTTP_201_CREATED)
        
        return Response({ 
                "success": False,
                "message": "A server error occured",
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

    def list(self, request):
        queryset = self.get_queryset()
        serializer = ClinicSessionCardSerializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)
    

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        clinic_session = get_object_or_404(queryset, id=pk)
        serializer = ClinicSessionDetailsSerializer(clinic_session, context={"request": request})
        return Response(serializer.data)


    def partial_update(self, request, pk=None):
        queryset = self.get_queryset()
        clinic_session = get_object_or_404(queryset, id=pk)

        serializer = ClinicSessionWriteSerializer(
            clinic_session,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        c_session = serializer.save()

        return Response({
            "success": True,
            "message": "Clinic session updated successfully.",
            "id": c_session.id,
        }, status=status.HTTP_200_OK)
    

    def destroy(self, request, pk=None):
        queryset = self.get_queryset()
        clinic_session = get_object_or_404(queryset, id=pk)

        clinic_session.delete()

        return Response({
            "success": True,
            "message": "Clinic session deleted successfully.",
        }, status=status.HTTP_204_NO_CONTENT)


# WorkingHours ViewSet
class WorkingHoursViewset(viewsets.ViewSet):

    CACHE_PREFIX = "branch_working_hours"
    permission_classes = [ IsProvider, IsAuthenticated ]

    def get_queryset(self):
        user = self.request.user
        branch_id = self.request.query_params.get("branch_id")

        queryset = OperatingHours.objects.all()

        if not branch_id:
            raise ValidationError("Branch id is required.")
        
        return queryset.filter(branch__id=branch_id, branch__provider__owner=user)


    def create(self, request):
        user = self.request.user
        branch_id = self.request.query_params.get("branch_id")
        branch = ProviderBranch.objects.get(id=branch_id)

        serializer = BranchOperatingHoursBulkSerializer(data=request.data, context={"branch": branch})
        if serializer.is_valid():
            serializer.save()

            GlobalCache().clear_cache(self.CACHE_PREFIX, user.id)

            return Response({
                "success": True,
                "message": "Working hours saved successfully."
            }, status=status.HTTP_201_CREATED)

        
        return Response({
                "success": False,
                "message": "A network error occured"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def list(self, request):
        user = self.request.user

        cache_key = GlobalCache().get_list_cache_key(self.CACHE_PREFIX, user.id)
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        queryset = self.get_queryset()
        data = BranchOperatingHoursReadSerializer(queryset, many=True).data

        cache.set(cache_key, data, timeout=GlobalCache().DEFAULT_TIMEOUT)

        return Response(data)


    def retrieve(self, request, pk=None):
        user = self.request.user
        

        cache_key = GlobalCache().get_detail_cache_key(self.CACHE_PREFIX, user.id, pk)
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)
        
        queryset = self.get_queryset()
        working_hour = get_object_or_404(queryset, id=pk)
        data = BranchOperatingHoursReadSerializer(working_hour).data

        cache.set(cache_key, data, timeout=GlobalCache().DEFAULT_TIMEOUT)

        return Response(data)



    def partial_update(self, request, pk=None):
        user = self.request.user
        queryset = self.get_queryset()

        working_hour = get_object_or_404(queryset, id=pk)
        serializer = BranchOperatingHoursBulkSerializer(working_hour, data=request.data, partial=True, context={"professional": user.professional_profile})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        GlobalCache().clear_cache(self.CACHE_PREFIX, user.id, pk)

        return Response({
            "success": True,
            "message": "Hours updated successfully.",
        }, status=status.HTTP_202_ACCEPTED)


    def destroy(self, request, pk=None):
        user = self.request.user
        queryset = self.get_queryset()

        working_hour = get_object_or_404(queryset, id=pk)

        working_hour.delete()

        GlobalCache().clear_cache(self.CACHE_PREFIX, user.id, pk)

        return Response({
            "success": True,
            "message": "Hours deleted successfully.",
        }, status=status.HTTP_204_NO_CONTENT)


#HospitalProfileView 
class HospitalProfileViewSet(viewsets.ViewSet):

    permission_classes = [IsAuthenticated, IsProvider]

    def get_branch(self, branch_id, user):
        return get_object_or_404(
            ProviderBranch,
            id=branch_id,
            provider__owner=user,
        )

    def create(self, request):

        branch_id = request.query_params.get("branch_id")

        if not branch_id:
            return Response(
                {"detail": "Branch is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        branch = self.get_branch(branch_id, self.request.user)

        if hasattr(branch, "hospital_profile"):
            return Response(
                {"detail": "Hospital profile already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = HospitalProfileWriteSerializer(
            data=request.data
        )

        if serializer.is_valid():

            hospital_profile = serializer.save(branch=branch)

            return Response({
                "success": True,
                "message": "Profile created successfully."
            },status=status.HTTP_201_CREATED)
        
        
        return Response({
            "success": False,
            "message": "An error occured",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):

        branch = self.get_branch(pk, request.user)

        hospital_profile = getattr(
            branch,
            "hospital_profile",
            None
        )

        if not hospital_profile:
            return Response(
                {"detail": "Hospital profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = HospitalProfileReadSerializer(
            hospital_profile
        )

        return Response(serializer.data)

    def partial_update(self, request, pk=None):

        branch = self.get_branch(pk, request.user)

        hospital_profile = getattr(
            branch,
            "hospital_profile",
            None
        )

        if not hospital_profile:
            return Response(
                {"detail": "Hospital profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = HospitalProfileWriteSerializer(
            hospital_profile,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(
            HospitalProfileReadSerializer(
                hospital_profile
            ).data
        )
