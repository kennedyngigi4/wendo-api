from django.utils import timezone
from rest_framework import serializers
from apps.providers.models.models import *
from apps.providers.models.hospital_profile_models import HospitalProfile, HospitalWard
from apps.reviews.serializers.serializers import ReviewReadSerializer
from apps.services.serializers.serializers import ServiceOfferingCardReadSerializer
from apps.providers.serializers.serializers import ClinicSessionDetailsSerializer
from apps.providers.serializers.serializers import BranchOperatingHoursReadSerializer

class HospitalProfileSerializer(serializers.ModelSerializer):
    level_display = serializers.CharField(source="get_level_display", read_only=True)
    trust_reasons = serializers.SerializerMethodField()

    class Meta:
        model = HospitalProfile
        fields = [
            "id", "ownership_type", "level", "level_display", "accepts_nhif", "year_established", "total_beds", "icu_beds",
            "has_emergency", "has_ambulance", "trust_reasons"
        ]

    def get_trust_reasons(self, obj):
        trust_map = {
            "friendly_staff": "Friendly & Caring Staff",
            "short_waiting_time": "Short Waiting Time",
            "affordable_services": "Affordable Healthcare Services",
            "insurance_accepted": "Insurance Accepted",
            "experienced_doctors": "Experienced Doctors",
            "clean_environment": "Clean & Comfortable Environment",
            "quality_patient_care": "Quality Patient Care",
            "fast_service": "Fast & Efficient Service",
            "modern_equipment": "Modern Medical Equipment",
            "privacy_confidentiality": "Patient Privacy & Confidentiality",
            "open_weekends": "Open on Weekends",
            "24_7_services": "24/7 Medical Services",
            "laboratory_services": "Laboratory Services Available",
            "pharmacy_available": "On-Site Pharmacy Available",
            "specialist_consultations": "Specialist Consultations Available",
        }

        return [
            trust_map.get(reason, reason)
            for reason in (obj.trust_reasons or [])
        ]


class HospitalWardSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalWard
        fields = [
            "id", "branch", "total_beds", "available_beds", "is_active", "price_per_day"
        ]


class ProviderReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = [
            "id", "name", "slug", "provider_type", "email", "website", "country", "logo", "description", "is_verified"
        ]



class ProviderBranchCardSerializer(serializers.ModelSerializer):
    provider = serializers.CharField(source="provider.name", read_only=True)
    banner = serializers.SerializerMethodField()
    is_open = serializers.SerializerMethodField()
    accepts_nhif = serializers.CharField(source="hospital_profile.accepts_nhif", read_only=True)
    rating = serializers.FloatField(source="avg_rating", read_only=True)
    availability = serializers.SerializerMethodField()

    class Meta:
        model = ProviderBranch
        fields = [
            "id", "name", "slug", "banner", "location_name", "phone", "is_verified", "provider", 
            "is_open", "accepts_nhif", "rating", "availability"
        ]

    def get_banner(self, obj):
        request = self.context.get("request")
        if obj.banner and request:
            return request.build_absolute_uri(obj.banner.url)
        elif not obj.banner:
            return request.build_absolute_uri(obj.provider.banner.url)
        else:
            return None

    def get_is_open(self, obj):
        now = timezone.localtime(timezone.now())
        current_day = now.weekday()
        current_time = now.time()

        hours = obj.operating_hours.filter(day_of_week=current_day).first()

        if not hours:
            return False

        if hours.is_closed:
            return False

        if hours.is_24:
            return True

        return hours.open_time <= current_time <= hours.close_time


    def get_availability(self, obj):

        now = timezone.now()
        current_day = now.isoweekday()
        current_time = now.time()

        today_schedule = obj.operating_hours.filter(
            day_of_week=current_day
        ).first()

        if not today_schedule:
            return {
                "available": False,
                "message": "No schedule available"
            }
        
        if today_schedule.is_closed:
            return {
                "available": False,
                "message": "Closed today"
            }
        
        if today_schedule.is_24:
            return {
                "available": True,
                "message": "Open 24 hours"
            }
        
        open_time = today_schedule.open_time
        close_time = today_schedule.close_time

        if open_time <= current_time <= close_time:
            return {
                "available": True,
                "open_time": open_time.strftime("%I:%M %p"),
                "close_time": close_time.strftime("%I:%M %p"),
                "message": f"Available until {close_time.strftime('%I:%M %p')}"
            }

        # Before opening
        if current_time < open_time:
            return {
                "available": False,
                "open_time": open_time.strftime("%I:%M %p"),
                "close_time": close_time.strftime("%I:%M %p"),
                "message": f"Opens at {open_time.strftime('%I:%M %p')}"
            }

        # After closing
        return {
            "available": False,
            "open_time": open_time.strftime("%I:%M %p"),
            "close_time": close_time.strftime("%I:%M %p"),
            "message": "Closed"
        }








class ProviderBranchDetailsSerializer(serializers.ModelSerializer):

    provider = ProviderReadSerializer(read_only=True)
    banner = serializers.SerializerMethodField()
    is_open = serializers.SerializerMethodField()
    profile = HospitalProfileSerializer(source="hospital_profile", read_only=True)
    ward = HospitalWardSerializer(source="hospital_wards", read_only=True)
    rating = serializers.FloatField(source="avg_rating", read_only=True)
    reviews_count = serializers.IntegerField(source="total_reviews", read_only=True)
    services = ServiceOfferingCardReadSerializer(source="branch_services", many=True, read_only=True)
    clinics = ClinicSessionDetailsSerializer(source="clinic_sessions", many=True, read_only=True)
    operating_hours = BranchOperatingHoursReadSerializer(many=True, read_only=True)
    reviews = ReviewReadSerializer(many=True, read_only=True)

    class Meta:
        model = ProviderBranch
        fields = [ 
            "id", "name", "slug", "banner", "location_name", "latitude", "longitude", "phone", "is_verified", "provider", "is_open", 
            "profile", "ward", "rating", "reviews_count", "services", "clinics", "operating_hours", "reviews"
        ]

    def get_banner(self, obj):
        request = self.context.get("request")
        if obj.banner and request:
            return request.build_absolute_uri(obj.banner.url)
        elif not obj.banner:
            return request.build_absolute_uri(obj.provider.banner.url)
        else:
            return None
        
    

    def get_is_open(self, obj):
        now = timezone.localtime(timezone.now())
        current_day = now.weekday()
        current_time = now.time()

        hours = obj.operating_hours.filter(day_of_week=current_day).first()

        if not hours:
            return False

        if hours.is_closed:
            return False

        if hours.is_24:
            return True

        return hours.open_time <= current_time <= hours.close_time




