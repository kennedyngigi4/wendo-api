from rest_framework.permissions import BasePermission
from apps.accounts.models.models import User


class IsPatient(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == "patient"
        )
    

class IsProvider(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role == "provider"
        )
