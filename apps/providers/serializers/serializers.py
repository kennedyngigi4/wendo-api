from rest_framework import serializers
from apps.professionals.models.models import *
from apps.providers.models.models import *
from apps.providers.models.hospital_profile_models import *


#=====================================================================================
# MANAGEMENT SERIALIZERS
#=====================================================================================



#=====================================================================================
# OWNER SERIALIZERS
#=====================================================================================

class ProviderDashboardSerializer(serializers.ModelSerializer):
    provider_type = serializers.CharField(source="provider.provider_type", read_only=True)

    class Meta:
        model = ProviderBranch
        fields = [
            "id", "name", "provider_type"
        ]


class ProfessionalDashboardSerializer(serializers.ModelSerializer):

    class Meta:
        model = Professional
        fields = [
            "id", "name"
        ]




class ProviderOwnerWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = [
            "name", "provider_type", "email", "website", "country", "description", "logo", "banner"
        ]


class ProviderOwnerListSerializer(serializers.ModelSerializer):
    total_branches = serializers.IntegerField(read_only=True)
    logo = serializers.SerializerMethodField()

    class Meta:
        model = Provider
        fields = [
            "id", "name", "provider_type", "email", "logo", "total_branches"
        ]


    def get_logo(self, obj):
        request = self.context.get("request")

        if obj.logo:
            return request.build_absolute_uri(obj.logo.url)
        return None


class ProviderBranchOwnerWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderBranch
        fields = [
            "provider", "name", "email", "phone", "emergency_phone", "location_name", "latitude", "longitude", "is_main_branch"
        ]


class ProviderBranchOwnerListSerializer(serializers.ModelSerializer):
    provider = serializers.CharField(source="provider.name", read_only=True)
    class Meta:
        model = ProviderBranch
        fields = [
            "id", "provider", "name", "phone","location_name", "latitude", "longitude", "is_main_branch"
        ]



# DEFAULT DASHBOARD SERIALIZERS
class DefaultDashBranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderBranch
        fields = [
            "id", "name", "is_active", "is_main_branch", "is_verified"
        ]


class DefaultDashProviderSerializer(serializers.ModelSerializer):

    logo = serializers.SerializerMethodField()

    class Meta:
        model = Provider
        fields = [
            "id", "name", "logo"
        ]


    def get_logo(self, obj):
        request = self.context.get("request")
        if not obj.logo:
            return None
        return request.build_absolute_uri(obj.logo.url)
    

class DefaultDashProfessionalSerializer(serializers.ModelSerializer):
    professional_type = serializers.CharField(source="professional_type.name", read_only=True)
    profile_photo = serializers.SerializerMethodField()

    class Meta:
        model = Professional
        fields = [
            "id", "name", "profile_photo", "professional_type"
        ]

    def get_profile_photo(self, obj):
        request = self.context.get("request")
        if not obj.profile_photo:
            return None
        return request.build_absolute_uri(obj.profile_photo.url)


# BRANCH SPECIALISTS
class SpecialistWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialist
        fields = [
            "title", "name", "photo", "specialties", "bio", "branch", "profession"
        ]

class SpecialistReadCardSerializer(serializers.ModelSerializer):

    photo = serializers.SerializerMethodField()
    profession = serializers.CharField(source="profession.name", read_only=True)

    class Meta:
        model = Specialist
        fields = [
            "id", "title", "name", "photo", "profession",
        ]

    def get_photo(self, obj):
        request = self.context.get("request")
        if obj.photo:
            return request.build_absolute_uri(obj.photo.url)
        return None


class SpecialistReadDetailsSerializer(serializers.ModelSerializer):

    photo = serializers.SerializerMethodField()

    class Meta:
        model = Specialist
        fields = [
            "id", "title", "name", "photo", "specialties", "profession", "bio", "branch", "slug"
        ]

    def get_photo(self, obj):
        request = self.context.get("request")
        if obj.photo:
            return request.build_absolute_uri(obj.photo.url)
        return None


# BRANCH CLINIC SESSIONS
class ClinicSessionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicSession
        fields = [
            "title", "branch", "consultation_fee", "specialists", "days_of_week", "banner", "description", 
            "start_time", "end_time", "start_date", "end_date"
        ]


class ClinicSessionCardSerializer(serializers.ModelSerializer):

    banner = serializers.SerializerMethodField()

    class Meta:
        model = ClinicSession
        fields = [
            "id", "slug", "title", "consultation_fee", "days_of_week", "banner", "description"
        ]

    def get_banner(self, obj):
        request = self.context.get("request")
        if obj.banner:
            return request.build_absolute_uri(obj.banner.url)
        return None


class ClinicSessionDetailsSerializer(serializers.ModelSerializer):

    banner = serializers.SerializerMethodField()

    class Meta:
        model = ClinicSession
        fields = [
            "id", "slug", "title", "branch", "consultation_fee", "specialists", "days_of_week", "banner", "description", 
            "start_time", "end_time", "start_date", "end_date"
        ]

    def get_banner(self, obj):
        request = self.context.get("request")
        if obj.banner:
            return request.build_absolute_uri(obj.banner.url)
        return None



class BranchOperatingHoursItemSerializer(serializers.Serializer):

    day = serializers.IntegerField()

    from_time = serializers.CharField( required=False, allow_blank=True)
    to_time = serializers.CharField( required=False, allow_blank=True)

    is_closed = serializers.BooleanField(default=False)
    is_24 = serializers.BooleanField(default=False)

    def validate(self, attrs):

        is_closed = attrs.get("is_closed")
        is_24 = attrs.get("is_24")

        open_time = attrs.get("from_time")
        close_time = attrs.get("to_time")

        # Cannot be both
        if is_closed and is_24:
            raise serializers.ValidationError(
                "A day cannot be closed and 24 hours."
            )

        # Normal working day
        if not is_closed and not is_24:

            if not open_time:
                raise serializers.ValidationError({
                    "from_time": "Opening time is required."
                })

            if not close_time:
                raise serializers.ValidationError({
                    "to_time": "Closing time is required."
                })

        return attrs
    


class BranchOperatingHoursBulkSerializer(serializers.Serializer):

    working_hours = BranchOperatingHoursItemSerializer(many=True)

    def create(self, validated_data):

        branch = self.context["branch"]
        working_hours = validated_data["working_hours"]

        OperatingHours.objects.filter(branch=branch).delete()

        objects = []

        for item in working_hours:

            is_closed = item.get("is_closed")
            is_24 = item.get("is_24")

            open_time = None
            close_time = None

            if not is_closed and not is_24:
                open_time = item.get("from_time")
                close_time = item.get("to_time")

            objects.append(
                OperatingHours(
                    branch=branch,
                    day_of_week=item["day"],
                    open_time=open_time,
                    close_time=close_time,
                    is_closed=is_closed,
                    is_24=is_24,
                )
            )

        return OperatingHours.objects.bulk_create(objects)




class BranchOperatingHoursReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = OperatingHours
        fields = [
            "id",
            "day_of_week",
            "open_time",
            "close_time",
            "is_24",
            "is_closed",
        ]

