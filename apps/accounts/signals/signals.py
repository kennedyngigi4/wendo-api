from django.dispatch import receiver
from django.db.models.signals import post_save


from apps.accounts.models.models import User
from apps.accounts.models.profile_models import PatientProfile, ProviderProfile



@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):

    if created:
        print(instance.role)

        if instance.role == "patient":
            PatientProfile.objects.create(
                user=instance
            )

        elif instance.role == "provider":
            ProviderProfile.objects.create(
                user=instance
            )
