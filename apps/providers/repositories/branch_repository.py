
from apps.providers.models.models import Provider, ProviderBranch

class BranchRepository:

    @staticmethod
    def get_branch_by_id(user, branch_id):
        return (
            ProviderBranch.objects
            .prefetch_related("hospital_profile")
            .filter(
                provider__owner=user, 
                id=branch_id
            ).first()
        )
    

    @staticmethod
    def get_by_owner(user):
        return (
            ProviderBranch.objects.filter(
                provider__owner=user, 
            ).first()
        )


    @staticmethod
    def get_branches(user):
        return ProviderBranch.objects.filter(
            provider__owner=user
        ).select_related(
            "provider"
        )
    

    @staticmethod
    def create_branch(provider, **validated_data):

        return (
            ProviderBranch.objects.create(
                provider=provider,
                **validated_data
            )
        )
    

    @staticmethod
    def update_branch(branch, **validated_data):

        for field, value in validated_data.items():
            setattr(branch, field, value)

        branch.save()
        return branch



    @staticmethod
    def delete_branch(branch):
        branch.delete()




