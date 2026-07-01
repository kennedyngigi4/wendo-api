from rest_framework import serializers

from apps.professionals.models.models import Professional
from apps.providers.models.models import ProviderBranch
from apps.reviews.models.models import Review



class ReviewWriteSerializer(serializers.ModelSerializer):

    provider_type = serializers.CharField(max_length=255, write_only=True)
    provider_id = serializers.CharField(max_length=255, write_only=True)

    class Meta:
        model = Review
        fields = [
            "id", "rating", "comment", "provider_type", "provider_id"
        ]

    def create(self, validated_data):

        provider_type = validated_data.pop("provider_type")
        provider_id = validated_data.pop("provider_id")

        review = Review(**validated_data)

        if provider_type == "professional":
            review.professional = Professional.objects.get(id=provider_id)

        elif provider_type == "hospital" or provider_type == "clinic":
            review.provider_branch = ProviderBranch.objects.get(id=provider_id)
        
        else:
            raise serializers.ValidationError({
                "provider_type": "Invalid provider type."
            })

        review.save()
        return review
    

class PatientReviewListSerializer(serializers.ModelSerializer):

    provider_branch = serializers.CharField(source="provider_branch.name", read_only=True)
    professional = serializers.CharField(source="professional.name", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id", "rating", "comment", "created_at", "provider_branch", "professional"
        ]


class ReviewReadSerializer(serializers.ModelSerializer):

    created_by = serializers.CharField(source="created_by.fullname", read_only=True) 

    class Meta:
        model = Review
        fields = [
            "id", "rating", "comment", "created_at", "created_by"
        ]
