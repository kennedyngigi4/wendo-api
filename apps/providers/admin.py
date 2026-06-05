from django.contrib import admin
from apps.providers.models.models import *
from apps.providers.models.hospital_profile_models import HospitalProfile, HospitalWard, Specialist, ClinicSession

# Register your models here.

admin.site.register(Provider)
admin.site.register(ProviderBranch)
admin.site.register(OperatingHours)
admin.site.register(HospitalProfile)
admin.site.register(HospitalWard)
admin.site.register(Specialist)
admin.site.register(ClinicSession)

