from django.shortcuts import render


from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.notifications.models import Notification, NewsletterSubscriber 
from apps.notifications.serializers.serializers import NewsletterSubscriberSerializer
# Create your views here.


class NewsletterSubscriptionView(APIView):

    def post(self, request):
        serializer = NewsletterSubscriberSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Subscription successful."
            }, status=status.HTTP_201_CREATED)
        



