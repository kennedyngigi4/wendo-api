from django.shortcuts import render, get_object_or_404

from rest_framework import status, generics, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from apps.accounts.permissions import IsProvider
from apps.bookings.models.models import Booking
from apps.bookings.serializers.serializers import BookingCardSerializer, BookingWriteSerializer



# Create your views here.


class PatientBookingsViewset(viewsets.ViewSet):
    """
        User bookings views i.e create, list, edit, delete
    """

    def create(self, request):

        print(request.data)
        serializer = BookingWriteSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({ "success": True, "message": "Booking successful"}, status=status.HTTP_201_CREATED)
        
        print(serializer.errors)
        return Response({ "success": False, "message": "A server error occured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        

    

class ProviderProfessionalBookingsViewset(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsProvider]

    def get_queryset(self):
        owner = self.request.query_params.get("owner_type")
        user = self.request.user

        queryset = Booking.objects.all()

        if owner == "provider":
            provider_id = self.request.query_params.get("provider_id")
            if not provider_id:
                raise ValidationError("Provider id is required.")

            return queryset.filter(
                provider__id=provider_id,
                provider__owner=user
            )

        elif owner == "branch":
            branch_id = self.request.query_params.get("branch_id")
            if not branch_id:
                raise ValidationError("Branch id is required.")

            return queryset.filter(
                branch__id=branch_id,
                branch__provider__owner=user
            )

        elif owner == "professional":
            professional_id = self.request.query_params.get("professional_id")
            if not professional_id:
                raise ValidationError("Professional id is required.")

            return queryset.filter(
                professional__id=professional_id,
                professional__user=user
            )

        raise ValidationError("Invalid or missing context")

    def list(self, request):
        queryset = self.get_queryset()
        serializer = BookingCardSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        booking = get_object_or_404(queryset, id=pk)

        serializer = BookingCardSerializer(booking)
        return Response(serializer.data)

    def partial_update(self, request, pk=None):

        queryset = self.get_queryset()
        booking = get_object_or_404(queryset, id=pk)

        serializer = BookingWriteSerializer(
            booking,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "success": True,
            "message": "Booking updated successfully",
            "data": serializer.data
        })

