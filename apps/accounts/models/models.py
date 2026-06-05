import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
# Create your models here.


class UserManager(BaseUserManager):
    
    def create_user(self, email, fullname, phone, role, password=None, **extra_fields):

        if not email:
            raise ValueError("Email is required")
        
        email = self.normalize_email(email).lower()
        user = self.model(
            email=email,
            fullname=fullname,
            phone=phone,
            role=role,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)

        return user
    

    def create_superuser(self, email, fullname, phone, role, password=None, **extra_fields):

        extra_fields.setdefault("is_admin", True)
        extra_fields.setdefault("is_superuser", True)

        user = self.create_user(
            email=email,
            fullname=fullname,
            phone=phone,
            password=password,
            role=role,
            **extra_fields
        )
        user.save(using=self._db)

        return user



class User(AbstractBaseUser, PermissionsMixin):

    CLIENT_ROLES = [
        ( "provider", "Provider"),
        ( "patient", "Patient"),
    ]

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)

    email = models.EmailField(unique=True)
    fullname = models.CharField(max_length=70)
    phone = models.CharField(max_length=15)

    role = models.CharField(max_length=50, choices=CLIENT_ROLES)

    date_joined = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "fullname", "phone", "role"
    ]


    def is_staff(self):
        return self.is_admin

    def __str__(self):
        return f"{self.fullname} ({self.email})"
