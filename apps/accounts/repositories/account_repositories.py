from rest_framework.exceptions import ValidationError, AuthenticationFailed

from apps.accounts.models.models import User


class AccountRepository:

    @staticmethod
    def email_exists(email):
        return User.objects.filter(email=email).exists()

    @staticmethod
    def create_account(data):
        return User.objects.create_user(
            email=data["email"],
            fullname=data["fullname"],
            phone=data["phone"],
            role=data["role"],
            password=data["password"],
        )

    @staticmethod
    def get_user_by_email(email):
        try:
            return User.objects.get(email=email)
        except:
            return None


    @staticmethod
    def validate_provider(user):
        if user.role == "provider":
            profile = user.providerprofile

            if not profile.email_verified:
                raise AuthenticationFailed("Verify your email")

            if not profile.is_approved:
                raise AuthenticationFailed("Your account is under review")

            if profile.is_suspended:
                raise AuthenticationFailed("Account suspended")

