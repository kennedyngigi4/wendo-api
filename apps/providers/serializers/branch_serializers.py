from rest_framework import serializers
from apps.providers.models.models import ProviderBranch, Provider, OperatingHours
from apps.providers.models.hospital_profile_models import HospitalProfile


#===============================================================
# PROVIDER BRANCH SERIALIZERS
#===============================================================

class HospitalProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = HospitalProfile
        fields = [
            "ownership_type", "level", "accepts_nhif", "year_established", "has_pharmacy",
            "total_beds", "icu_beds", "has_emergency", "has_ambulance",
            "facebook", "instagram", "linkedin", "youtube", "twitter_x", "tiktok",
        ]


class HospitalProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalProfile
        fields = [
            "ownership_type", "level", "accepts_nhif", "year_established", "has_pharmacy",
            "total_beds", "icu_beds", "has_emergency", "has_ambulance",
            "facebook", "instagram", "linkedin", "youtube", "twitter_x", "tiktok",
        ]


class BranchUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ProviderBranch
        fields = [
            "name", "phone", "email", "bookings_email", "country", "location_name",
            "latitude", "longitude", "building_floor", "banner", "is_main_branch",
            "emergency_phone"
        ]


class BranchWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderBranch
        fields = [
            "provider","name", "email", "phone", "emergency_phone", "location_name", "latitude", "longitude", 
            "is_main_branch", "country", "building_floor", "banner", "bookings_email"
        ]




class BranchListSerializer(serializers.ModelSerializer):

    provider_name = serializers.CharField(source="provider.name", read_only=True)

    class Meta:
        model = ProviderBranch
        fields = [
            "id", "provider", "name", "phone","location_name", "is_main_branch",
            "provider_name",
        ]



class BranchDetailSerializer(serializers.ModelSerializer):

    hospital_profile = HospitalProfileSerializer(read_only=True)

    class Meta:
        model = ProviderBranch
        fields = [
            "id", "name", "phone", "country", "location_name", "latitude", "longitude", "is_main_branch", "banner",
            "building_floor", "email", "bookings_email", "hospital_profile",
        ]

