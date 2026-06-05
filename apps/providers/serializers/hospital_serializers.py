from rest_framework import serializers
from apps.providers.models.hospital_profile_models import HospitalProfile

TRUST_REASON_CHOICES = [
    ("friendly_staff", "Friendly & Caring Staff"),
    ("short_waiting_time", "Short Waiting Time"),
    ("affordable_services", "Affordable Healthcare Services"),
    ("insurance_accepted", "Insurance Accepted"),
    ("experienced_doctors", "Experienced Doctors"),
    ("clean_environment", "Clean & Comfortable Environment"),
    ("quality_patient_care", "Quality Patient Care"),
    ("fast_service", "Fast & Efficient Service"),
    ("modern_equipment", "Modern Medical Equipment"),
    ("privacy_confidentiality", "Patient Privacy & Confidentiality"),
    ("open_weekends", "Open on Weekends"),
    ("24_7_services", "24/7 Medical Services"),
    ("laboratory_services", "Laboratory Services Available"),
    ("pharmacy_available", "On-Site Pharmacy Available"),
    ("specialist_consultations", "Specialist Consultations Available"),
]

VALID_TRUST_REASONS = {
    choice[0] for choice in TRUST_REASON_CHOICES
}


class HospitalProfileWriteSerializer(serializers.ModelSerializer):

    trust_reasons = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )

    class Meta:
        model = HospitalProfile
        fields = [
            "ownership_type", "level", "accepts_nhif", "year_established", "has_pharmacy","total_beds",
            "icu_beds", "has_emergency", "has_ambulance", "trust_reasons", 
        ]

    def validate_trust_reasons(self, value):

        if len(value) > 4:
            raise serializers.ValidationError(
                "Maximum 4 trust reasons allowed."
            )

        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                "Duplicate trust reasons are not allowed."
            )

        invalid_items = [
            item for item in value
            if item not in VALID_TRUST_REASONS
        ]

        if invalid_items:
            raise serializers.ValidationError(
                f"Invalid trust reasons: {invalid_items}"
            )

        return value



class HospitalProfileReadSerializer(serializers.ModelSerializer):

    trust_reason_labels = serializers.SerializerMethodField()

    class Meta:
        model = HospitalProfile
        fields = "__all__"

    def get_trust_reason_labels(self, obj):

        mapping = dict(HospitalProfile.TRUST_REASON_CHOICES)

        return [
            {
                "id": item,
                "name": mapping.get(item, item)
            }
            for item in obj.trust_reasons
        ]

