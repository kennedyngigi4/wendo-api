from django.shortcuts import render

from rest_framework import status, generics, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from apps.reviews.models.models import Review
from apps.reviews.serializers.serializers import ReviewReadSerializer, ReviewWriteSerializer

# Create your views here.

class PatientReviewView(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    def create(self, request):

        user = self.request.user

        serializer = ReviewWriteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=user)

            return Response({ "success": True, "message": "Review successful."}, status=status.HTTP_201_CREATED)
        
        
        return Response({ "success": False, "error": "A server error occured."}, status=status.HTTP_400_BAD_REQUEST)


    def list(self, request):

        user = self.request.user
        




