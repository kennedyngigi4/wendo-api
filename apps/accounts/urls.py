from django.urls import path
from apps.accounts.views.views import *


urlpatterns = [
    path( "register/", RegisterView.as_view(), name="register"),
    path( "login/", LoginView.as_view(), name="login"),

    path( "forgot_password/",  ForgotPasswordView.as_view(),  name="forgot_password" ),
    path( "reset_password/", ResetPasswordView.as_view(), name="reset_password" ),
]


