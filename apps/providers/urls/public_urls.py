from django.urls import path
from apps.providers.views.public_views import *


# Public endpoints
urlpatterns = [
    path( "all/<str:provider_page>/", AllProvidersViewSet.as_view(), name="all_providers"),
    path( "details/<str:slug>/",ProviderDetailsView.as_view(), name="details")
]

