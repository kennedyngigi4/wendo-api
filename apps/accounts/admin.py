from django.contrib import admin

from apps.accounts.models.models import User
from apps.accounts.models.profile_models import PatientProfile, ProviderProfile

# Register your models here.
admin.site.register(User)
admin.site.register(PatientProfile)
admin.site.register(ProviderProfile)

