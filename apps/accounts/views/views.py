import traceback
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from rest_framework import status, generics, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.permissions import IsAuthenticated

from apps._core_utils.services.email_services import EmailService
from apps.accounts.models.models import User
from apps.accounts.services.account_services import AccountService
from apps.accounts.serializers.serializers import *



# Create your views here.

class RegisterView(APIView):

    def post(self, request):
        
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()

            try:
                EmailService.send_welcome_email(user)
            except Exception as e:
                print("EMAIL ERROR:", str(e))
                traceback.print_exc()

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
        
        
class ForgotPasswordView(APIView):

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]


        try:
            user = User.objects.get(email=email)

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            reset_url = (
                f"https://wendohealth.com/auth/reset-password"
                f"?uid={uid}&token={token}"
            )


            EmailService.send_password_reset_email(
                user=user,
                reset_url=reset_url
            )

        except User.DoesNotExist:
            pass

        return Response({ 
            "success": True, 
            "message": "If an account exists, a reset link has been sent."
        }, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uid = serializer.validated_data["uid"]
        token = serializer.validated_data["token"]
        password = serializer.validated_data["password"]


        try:
            user_id = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=user_id)



        except Exception:
            return Response({
                "success": False,
                "errors": "Invalid reset link"
            }, status=status.HTTP_400_BAD_REQUEST)


        if not default_token_generator.check_token(user, token):
            return Response({
                "success": False,
                "errors": "Reset link expired or invalid"
            }, status=status.HTTP_400_BAD_REQUEST)


        user.set_password(password)
        user.save()


        return Response({
            "success": True,
            "message": "Password reset successfully."
        }, status=status.HTTP_200_OK)



class ProfileView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def retrieve(self, request):
        serializer = UserSerializer(self.request.user)
        return Response(serializer.data)

    def partial_update(self, request):

        serializer = UserSerializer(self.request.user, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({ "success": True, "data":  serializer.data}, status=status.HTTP_202_ACCEPTED)

    def destroy(self, request):
    
        user = self.request.user
        user.delete()

        return Response(
            {"detail": "Account deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )



