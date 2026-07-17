from django.db import transaction

from rest_framework.exceptions import ValidationError, NotFound

from apps.providers.models.models import Provider, ProviderBranch
from apps.providers.repositories.provider_repository import ProviderRepository
from apps.providers.models.hospital_profile_models import HospitalProfile
from apps.providers.repositories.branch_repository import BranchRepository


class BranchService:
    
    @staticmethod
    @transaction.atomic
    def create_branch(user, **validated_data):

        provider = validated_data.pop("provider")
        if provider.owner != user:
            raise ValidationError("Invalid provider.")
        
        branch = BranchRepository.create_branch(provider=provider, **validated_data)

        HospitalProfile.objects.create(
            branch=branch
        )


        return branch


    @staticmethod
    def get_branches(user):
        return BranchRepository.get_branches(user)


    @staticmethod
    def update_branch(user):
        return BranchRepository.get_branches(user)
    

    @staticmethod
    def get_branch(user, branch_id):

        branch = BranchRepository.get_branch_by_id(
            user,
            branch_id
        )


        if not branch:
            raise NotFound("Branch not found.")
        
        return branch
    

    @staticmethod
    @transaction.atomic
    def update_branch(user, branch_id, **validated_data):

        branch = BranchService.get_branch(
            user,
            branch_id
        )

        return BranchRepository.update_branch(
            branch,
            **validated_data
        )
    

    @staticmethod
    @transaction.atomic
    def delete_branch(user, branch_id):

        branch = BranchService.get_branch(
            user,
            branch_id
        )

        BranchRepository.delete_branch(branch)



