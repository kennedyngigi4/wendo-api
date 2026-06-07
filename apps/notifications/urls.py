from django.urls import path
from apps.notifications.views import NewsletterSubscriptionView

urlpatterns = [
    path("newsletter_subscription/", NewsletterSubscriptionView.as_view(), name="newsletter_subscription", )
]

