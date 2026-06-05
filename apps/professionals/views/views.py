from django.shortcuts import render, get_object_or_404
from django.core.cache import cache

from rest_framework import status, generics, viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action

from apps._core_utils.helpers.cache_utils import GlobalCache
from apps.accounts.permissions import *
from apps.professionals.models.models import *
from apps.professionals.serializers.serializers import *
from apps.professionals.serializers.public_serializers import *
from apps.professionals.services.professional_services import ProfessionalsServices


# Create your views here.
class ProfessionalTypesView(generics.ListAPIView):
    serializer_class = ProfessionalTypeSerializer
    queryset = ProfessionalType.objects.all().order_by("name")


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        professional = user.professional_profile 
        
        data = {
            "profile": ProfessionalsServices.get_profile(professional, request),
            "stats": ProfessionalsServices.get_stats(professional),
            "recent_reviews": ProfessionalsServices.get_reviews(professional),
            "availability": ProfessionalsServices.get_today_availability(professional),
            "upcoming_bookings": ProfessionalsServices.get_upcoming_bookings(professional),
            "subscription": ProfessionalsServices.get_latest_subscription(professional),
        }

        return Response(data)



class OldProfessionalViewSet(viewsets.ViewSet): 
    permission_classes = [ IsAuthenticated, IsProvider]
    parser_classes = [MultiPartParser, FormParser]

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        professional = Professional.objects.filter(user=self.request.user).first()

        if not professional:
            return Response({ "professional": None }, status=200)

        serializer = ProfessionalReadSerializer(professional)
        return Response({ "professional": serializer.data}, status=200)
    

    def create(self, request):
        user = self.request.user

        serializer = ProfessionalWriteSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
        
            serializer.save(user=user)

            return Response({ "success": True, "message": "Professional account created."}, status=status.HTTP_201_CREATED)

        print(serializer.errors)
        return Response({ "success": False, "message": "An server error occured."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    def partial_update(self, request, pk=None):
        pass


    def destroy(self, request, pk=None):
        pass


class ProfessionalViewSet(viewsets.ViewSet):

    permission_classes = [
        IsAuthenticated,
        IsProvider
    ]

    parser_classes = [
        MultiPartParser,
        FormParser
    ]

    # -----------------------------------
    # HELPERS
    # -----------------------------------

    def get_professional(self, request):

        return (
            Professional.objects
            .filter(user=request.user)
            .select_related("professional_type")
            .prefetch_related("specialties")
            .first()
        )

    def get_read_serializer(self, *args, **kwargs):

        return ProfessionalReadSerializer(*args,**kwargs)

    def get_write_serializer(self, *args, **kwargs):

        return ProfessionalWriteSerializer(
            *args,
            **kwargs
        )

    # -----------------------------------
    # CREATE
    # POST /professionals/profession/
    # -----------------------------------

    def create(self, request):

        existing = self.get_professional(request)

        if existing:
            return Response(
                {
                    "success": False,
                    "message": "Professional profile already exists."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_write_serializer(
            data=request.data
        )

        if serializer.is_valid():

            professional = serializer.save(
                user=request.user
            )

            return Response(
                {
                    "success": True,
                    "message": "Professional profile created successfully.",
                    "professional": self.get_read_serializer(
                        professional
                    ).data
                },
                status=status.HTTP_201_CREATED
            )

        print(serializer.errors)

        return Response(
            {
                "success": False,
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # -----------------------------------
    # RETRIEVE CURRENT USER PROFILE
    # GET /professionals/profession/me/
    # -----------------------------------

    @action( detail=False, methods=["get"], url_path="me")
    def me(self, request):

        professional = self.get_professional(
            request
        )

        if not professional:

            return Response(
                {
                    "professional": None
                },
                status=status.HTTP_200_OK
            )

        serializer = self.get_read_serializer(
            professional, context={"request": request}
        )

        return Response(
            {
                "professional": serializer.data
            },
            status=status.HTTP_200_OK
        )

    # -----------------------------------
    # PARTIAL UPDATE
    # PATCH /professionals/profession/update/
    # -----------------------------------

    @action(detail=False,  methods=["patch"], url_path="update" )
    def partial_update_profile(self, request):

        professional = self.get_professional(
            request
        )

        if not professional:

            return Response(
                {
                    "success": False,
                    "message": "Professional profile not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_write_serializer(
            professional,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():

            professional = serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Professional profile updated successfully.",
                    "professional": self.get_read_serializer(
                        professional
                    ).data
                },
                status=status.HTTP_200_OK
            )

        print(serializer.errors)

        return Response(
            {
                "success": False,
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # -----------------------------------
    # DELETE
    # DELETE /professionals/profession/delete/
    # -----------------------------------

    @action(detail=False,  methods=["delete"], url_path="delete")
    def delete_profile(self, request):

        professional = self.get_professional(
            request
        )

        if not professional:

            return Response(
                {
                    "success": False,
                    "message": "Professional profile not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        professional.delete()

        return Response(
            {
                "success": True,
                "message": "Professional profile deleted successfully."
            },
            status=status.HTTP_200_OK
        )



# Education ViewSet
class EducationViewset(viewsets.ViewSet):

    CACHE_PREFIX = "prof_education"
    permission_classes = [ IsAuthenticated, IsProvider ]


    def create(self, request):
        user = self.request.user

        professional = user.professional_profile
        serializer = ProfessionalWriteEducationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(professional=professional)

        GlobalCache().clear_cache(self.CACHE_PREFIX, user.id)

        return Response({
            "success": True,
            "message": "Education added successfully."
        }, status=status.HTTP_201_CREATED)
    


    def list(self, request):
        user = self.request.user

        cache_key = GlobalCache().get_list_cache_key(self.CACHE_PREFIX, user.id)
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)
        
        educations = Education.objects.filter(professional=user.professional_profile)
        data = ProfessionalReadEducationSerializer(educations, many=True).data

        cache.set(cache_key, data, timeout=GlobalCache().DEFAULT_TIMEOUT)

        return Response(data)

    
    def retrieve(self, request, pk=None):
        user = self.request.user
        
        cache_key = GlobalCache().get_detail_cache_key(self.CACHE_PREFIX, user.id, pk)
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)
        
        education = get_object_or_404(Education, professional=user.professional_profile, id=pk)
        data = ProfessionalReadEducationSerializer(education).data

        cache.set(cache_key, data, timeout=GlobalCache().DEFAULT_TIMEOUT)

        return Response(data)
    
    
    def partial_update(self, request, pk=None):
        user = self.request.user
        
        education = get_object_or_404(Education, professional=user.professional_profile, pk=None)
        serializer = ProfessionalWriteEducationSerializer(education, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        GlobalCache().clear_cache(self.CACHE_PREFIX, user.id, pk)

        return Response({
            "success": True,
            "message": "Education updated successfully.",
        }, status=status.HTTP_202_ACCEPTED)
    

    def destroy(self, request, pk=None):
        user = self.request.user
        
        education = get_object_or_404(Education, professional=user.professional_profile, pk=None)
        education.delete()

        GlobalCache().clear_cache(self.CACHE_PREFIX, user.id, pk)

        return Response({
            "success": True,
            "message": "Education deleted successfully."
        }, status=status.HTTP_204_NO_CONTENT)



# WorkingHours ViewSet
class WorkingHoursViewset(viewsets.ViewSet):

    CACHE_PREFIX = "prof_working_hours"
    permission_classes = [ IsProvider, IsAuthenticated ]

    def create(self, request):
        user = self.request.user

        serializer = OperatingHoursBulkSerializer(data=request.data, context={"professional": user.professional_profile})
        if serializer.is_valid():
            serializer.save(professional=user.professional_profile)

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

        queryset = OperatingHours.objects.filter(professional=user.professional_profile)
        data = OperatingHoursReadSerializer(queryset, many=True).data

        cache.set(cache_key, data, timeout=GlobalCache().DEFAULT_TIMEOUT)

        return Response(data)


    def retrieve(self, request, pk=None):
        user = self.request.user

        cache_key = GlobalCache().get_detail_cache_key(self.CACHE_PREFIX, user.id, pk)
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        working_hour = get_object_or_404(OperatingHours, professional=user.professional_profile, id=pk)
        data = OperatingHoursReadSerializer(working_hour).data

        cache.set(cache_key, data, timeout=GlobalCache().DEFAULT_TIMEOUT)

        return Response(data)



    def partial_update(self, request, pk=None):
        user = self.request.user

        working_hour = get_object_or_404(OperatingHours, professional=user.professional_profile, id=pk)
        serializer = OperatingHoursBulkSerializer(working_hour, data=request.data, partial=True, context={"professional": user.professional_profile})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        GlobalCache().clear_cache(self.CACHE_PREFIX, user.id, pk)

        return Response({
            "success": True,
            "message": "Hours updated successfully.",
        }, status=status.HTTP_202_ACCEPTED)


    def destroy(self, request, pk=None):
        user = self.request.user

        working_hour = get_object_or_404(OperatingHours, professional=user.professional_profile, id=pk)

        working_hour.delete()

        GlobalCache().clear_cache(self.CACHE_PREFIX, user.id, pk)

        return Response({
            "success": True,
            "message": "Hours deleted successfully.",
        }, status=status.HTTP_204_NO_CONTENT)

