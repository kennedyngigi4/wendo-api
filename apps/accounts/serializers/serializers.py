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



class PatientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientProfile
        fields = [
            "gender",
            "dob",
            "country",
            "profile_picture",
        ]


class UserSerializer(serializers.ModelSerializer):

    gender = serializers.CharField(source="patientprofile.gender")
    dob = serializers.DateField(source="patientprofile.dob")
    country = serializers.CharField(source="patientprofile.country")
    profile_picture = serializers.ImageField(
        source="patientprofile.profile_picture",
        required=False
    )

    class Meta:
        model = User
        fields = [
            "id", "email", "fullname", "phone", "role", "gender", "dob", "country", "profile_picture"
        ]

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("patientprofile", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if profile_data:
            profile, _ = PatientProfile.objects.get_or_create(user=instance)

            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(min_length=8)

