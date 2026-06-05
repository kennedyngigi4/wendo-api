from django.contrib import admin
from apps.services.models.models import Service, ServiceCategory, CustomService, Specialty, ServiceOffering

# Register your models here.
admin.site.register(Service)
admin.site.register(ServiceCategory)
admin.site.register(CustomService)
admin.site.register(Specialty)
admin.site.register(ServiceOffering)
