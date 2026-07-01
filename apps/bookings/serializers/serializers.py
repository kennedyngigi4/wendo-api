from rest_framework import serializers
from apps.bookings.models.models import Booking
from apps.services.models.models import ServiceOffering
from apps.services.serializers.serializers import ServiceOfferingCardReadSerializer


class BookingWriteSerializer(serializers.ModelSerializer):
    service = serializers.PrimaryKeyRelatedField(
        queryset=ServiceOffering.objects.all()
    )

    class Meta:
        model = Booking
        fields = [
            "name", "email", "phone", "appointment_date", "appointment_time", "service", "reason", "status"
        ]

    def create(self, validated_data):
        service = validated_data["service"]

        validated_data["provider"] = service.provider
        validated_data["branch"] = service.branch
        validated_data["professional"] = service.professional

        return super().create(validated_data)
    
    




class BookingCardSerializer(serializers.ModelSerializer):

    service = ServiceOfferingCardReadSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id", "name", "email", "phone", "status", "service", "status", "created_at", "updated_at", "appointment_date", "appointment_time", "reason"
        ]



class BookingPatientReadSerializer(serializers.ModelSerializer):

    service = ServiceOfferingCardReadSerializer(read_only=True)
    branch_name = serializers.CharField(source="branch.name", read_only=True)
    provider_name = serializers.CharField(source="provider.name", read_only=True)
    professional_name = serializers.CharField(source="professional.name", read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id", "appointment_date", "appointment_time", "status", "service", "created_at",
            "branch_name", "provider_name", "professional_name",
        ]



