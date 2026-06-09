from django.shortcuts import render

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from apps._core_utils.services.email_services import EmailService
from apps.accounts.models.models import User
from apps.accounts.services.account_services import AccountService
from apps.accounts.serializers.serializers import *



# Create your views here.

class RegisterView(APIView):

    def post(self, request):
        
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.save()
        
        try:
            EmailService.send_welcome_email(user)
        except Exception as e:
            print("EMAIL ERROR:", str(e))

        return Response({
            "success": True,
            "message": "Account created successfully"
        }, status=status.HTTP_201_CREATED)

        

class LoginThrottle(AnonRateThrottle):
    rate = "5/min"

class LoginView(APIView):
    throttle_classes = [LoginThrottle]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = AccountService.login_user(
            serializer.validated_data["email"], 
            serializer.validated_data["password"]
        )

        
        
        return Response({ 
            "success": True, 
            "data": result,
        }, status=status.HTTP_200_OK)
        
        


