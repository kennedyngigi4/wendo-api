from rest_framework import serializers

from apps.notifications.models import NewsletterSubscriber, Notification


class NewsletterSubscriberSerializer(serializers.ModelSerializer):

    class Meta:
        model = NewsletterSubscriber
        fields = [
            "email"
        ]

    
    def validate_email(self, value):
        email = value.lower().strip()

        if NewsletterSubscriber.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                "Email already subscribed."
            )

        return email

