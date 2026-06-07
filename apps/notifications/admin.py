from django.contrib import admin

from apps.notifications.models import NewsletterSubscriber, Notification
# Register your models here.

admin.site.register(Notification)
admin.site.register(NewsletterSubscriber)


