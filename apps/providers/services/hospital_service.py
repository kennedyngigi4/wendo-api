from django.shortcuts import get_object_or_404

from apps.providers.models.models import ProviderBranch
from apps.providers.models.hospital_profile_models import HospitalProfile

class HospitalProfileService:

    @staticmethod
    def update_profile(user, branch_id, **validated_data):

        branch = get_object_or_404(
            ProviderBranch.objects.select_related("hospital_profile"),
            id=branch_id,
            provider__owner=user,
        )

        profile = branch.hospital_profile

        for field, value in validated_data.items():
            setattr(profile, field, value)


        profile.save()
        return profile



