from django.utils import timezone

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError, AuthenticationFailed

from apps.accounts.models.models import User
from apps.accounts.repositories.account_repositories import AccountRepository


class AccountService:



    @staticmethod
    def register_user(data):
        email = data["email"].lower().strip()
        password = data["password"]

        if AccountRepository.email_exists(email):
            raise ValidationError("Account with this email exists.")
        
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters.")

        return AccountRepository.create_account({ **data, "email": email})
    


    @staticmethod
    def login_user(email, password):

        user = AccountRepository.get_user_by_email(email)

        if not user:
            raise AuthenticationFailed("Invalid credentials.")

        if not user.check_password(password):
            raise AuthenticationFailed("Invalid credentials.")
        
        if not user.is_active:
            raise AuthenticationFailed("Account disabled.")
        
        AccountRepository.validate_provider(user)

        refresh = RefreshToken.for_user(user)

        refresh["email"] = user.email
        refresh["role"] = user.role
        refresh["user_id"] = str(user.id)

        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        return {
            "id": user.id,
            "name": user.fullname,
            "email": user.email,
            "role": user.role,
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }



    @staticmethod
    def logout_user(refresh_token):
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return {"message": "Logged out"}
        except Exception:
            raise AuthenticationFailed("Invalid token.")


