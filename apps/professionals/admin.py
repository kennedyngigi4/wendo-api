from django.contrib import admin

from apps.professionals.models.models import *
# Register your models here.

admin.site.register(ProfessionalType)
admin.site.register(Professional)
admin.site.register(Education)
admin.site.register(OperatingHours)



