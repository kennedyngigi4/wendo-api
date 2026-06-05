from django.utils import timezone

from rest_framework import serializers
from apps.professionals.models.models import *
from apps.services.serializers.serializers import ServiceOfferingCardReadSerializer
from apps.professionals.serializers.serializers import OperatingHoursReadSerializer, ProfessionalReadEducationSerializer
from apps.reviews.serializers.serializers import ReviewReadSerializer


class ProfessionalTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfessionalType
        fields = [
            "id", "name", "icon", "slug"
        ]


class SpecialtySerializer(serializers.ModelSerializer):

    # professional_type = serializers.CharField(source="professional_type.name", read_only=True)

    class Meta:
        model = Specialty
        fields = [
            "id", "name", "professional_type", "slug"
        ]


class ProfessionalHomeSerializer(serializers.ModelSerializer):

    professional_type = serializers.CharField(source="professional_type.name", read_only=True)
    specialties = serializers.SerializerMethodField()
    profile_photo = serializers.SerializerMethodField()
    availability = serializers.SerializerMethodField()

    class Meta:
        model = Professional
        fields = [
            "id","slug", "name", "title", "years_of_experience", "professional_type", 
            "specialties", "profile_photo", "accepts_nhif", "availability"
        ]

    def get_profile_photo(self, obj):
        request = self.context.get("request")

        if obj.profile_photo:
            return request.build_absolute_uri(obj.profile_photo.url)
        return None
    
    def get_specialties(self, obj):
        return [s.name for s in obj.specialties.all()]
    
    
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




class ProfessionalCardSerializer(serializers.ModelSerializer):

    professional_type = serializers.CharField(source="professional_type.name", read_only=True)
    specialties = serializers.SerializerMethodField()
    profile_photo = serializers.SerializerMethodField()
    rating = serializers.FloatField(source="avg_rating",read_only=True)
    availability = serializers.SerializerMethodField()

    class Meta:
        model = Professional
        fields = [
            "id","slug", "name", "title", "years_of_experience", "professional_type", 
            "specialties", "profile_photo", "location_name", "consultation_fee", "rating",
            "availability"
        ]


    def get_profile_photo(self, obj):
        request = self.context.get("request")

        if obj.profile_photo:
            return request.build_absolute_uri(obj.profile_photo.url)
        return None
    

    def get_specialties(self, obj):
        return [s.name for s in obj.specialties.all()]
    

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



        




class ProfessionalDetailsSerializer(serializers.ModelSerializer):

    professional_type = serializers.CharField(source="professional_type.name", read_only=True)
    specialties = serializers.SerializerMethodField()
    profile_photo = serializers.SerializerMethodField()
    rating = serializers.FloatField(source="avg_rating", read_only=True)
    services = ServiceOfferingCardReadSerializer(source="professional_services", many=True, read_only=True)
    education = ProfessionalReadEducationSerializer(source="professional_education", many=True, read_only=True)
    operating_hours = OperatingHoursReadSerializer(many=True, read_only=True)
    reviews = ReviewReadSerializer(many=True, read_only=True)

    class Meta:
        model = Professional
        fields = [
            "id","slug", "name", "title", "years_of_experience", "professional_type", 
            "specialties", "profile_photo", "consultation_fee", "bio", "location_name", "latitude", "longitude",
            "gender", "phone", "email", "website", "accepts_nhif", "is_verified", "created_at",
            "rating", "services", "education", "operating_hours", "reviews"
        ]


    def get_profile_photo(self, obj):
        request = self.context.get("request")

        if obj.profile_photo:
            return request.build_absolute_uri(obj.profile_photo.url)
        return None
    

    def get_specialties(self, obj):
        return [s.name for s in obj.specialties.all()]


