from rest_framework import serializers
from apps.services.models.models import Service, ServiceCategory, CustomService, Specialty, ServiceOffering


class ServiceCategoryReadSearializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = [
            "id", "name", "slug", "icon"
        ]


class ServiceReadSearializer(serializers.ModelSerializer):

    category = ServiceCategoryReadSearializer(read_only=True)

    class Meta:
        model = Service
        fields = [
            "id", "name", "slug", "icon", "category", "is_active"
        ]


class CustomServiceReadSearializer(serializers.ModelSerializer):
    class Meta:
        model = CustomService
        fields = [
            "id", "name", "slug", "icon", "is_approved"
        ]




class SpecialtyReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialty
        fields = [
            "id", "slug", "name"
        ]

class ServiceOfferingWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceOffering
        fields = [
            "provider", "branch", "professional", "service", "service_category", "price", 
            "description", "is_available"
        ]


class ServiceOfferingCardReadSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source="service.name", read_only=True)
    service = ServiceReadSearializer(read_only=True)

    class Meta:
        model = ServiceOffering
        fields = [
            "id", "service", "service_name", "description"
        ]        


class ServiceOfferingReadSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source="service.name", read_only=True)
    class Meta:
        model = ServiceOffering
        fields = [
            "id", "provider", "branch", "professional", "service", "service_name", "service_category", "price", 
            "description", "is_available"
        ]
