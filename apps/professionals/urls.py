from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.professionals.views.views import *
from apps.professionals.views.public_views import *

router = DefaultRouter()
router.register( r"profession", ProfessionalViewSet, basename="profession" )
router.register( r"education", EducationViewset, basename="education" )
router.register( r"working_hours", WorkingHoursViewset, basename="working_hours" )
urlpatterns = router.urls


urlpatterns += [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]


# Public urls
urlpatterns += [
    path("types/", ProfessionalTypesView.as_view(), name="types"),
    path("home/", ProfessionalsHomeView.as_view(), name="home"),
    path("all/", AllProfessionalsView.as_view(), name="all"),
    path("professional_details/<str:slug>/", ProfessionalDetailsView.as_view(), name="professional_details"),
]


