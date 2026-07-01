from django.urls import path
from apps.accounts.views.views import *
from rest_framework.routers import DefaultRouter

# router = DefaultRouter()
# router.register(r"profile", ProfileView, basename="profile")
# urlpatterns = router.urls


profile = ProfileView.as_view({
    "get": "retrieve",
    "patch": "partial_update",
    "delete": "destroy",
})
urlpatterns = [
    path( "register/", RegisterView.as_view(), name="register"),
    path( "login/", LoginView.as_view(), name="login"),

    path( "forgot_password/",  ForgotPasswordView.as_view(),  name="forgot_password" ),
    path( "reset_password/", ResetPasswordView.as_view(), name="reset_password" ),

    path("profile", profile, name="profile"),
]


