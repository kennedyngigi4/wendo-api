from rest_framework import serializers

from apps.accounts.models.models import User
from apps.accounts.models.profile_models import *
from apps.accounts.services.account_services import AccountService


class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "email", "fullname", "phone", "password", "role"
        ]
        extra_kwargs = { "password": { "write_only": True}} 


    def create(self, validated_data):
        return AccountService.register_user(validated_data)
    


    def validate_email(self, value):
        email = value.lower().strip()

        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                "Email is already registered"
            )
        
        return email
    
    def validate_phone(self, value):
        phone = value.strip()

        if User.objects.filter(phone__iexact=phone).exists():
            raise serializers.ValidationError(
                "Phone number is already registered"
            )
        
        return phone



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()



class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "id", "email", "fullname", "phone", "role"
        ]




