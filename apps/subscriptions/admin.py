from django.contrib import admin

from apps.subscriptions.models.models import *


# Register your models here.
admin.site.register(Feature)
admin.site.register(Plan)
admin.site.register(PlanFeature)
admin.site.register(Subscription)
admin.site.register(Promotion)
admin.site.register(PromotionRedemption)
