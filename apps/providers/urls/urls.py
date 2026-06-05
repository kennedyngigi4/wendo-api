from django.urls import path
from apps.providers.views.views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"organizations", OrganizationsView, basename="organizations")
router.register(r"branches", BranchesViewSet, basename="branches")
router.register(r"branch_specialists", SpecialistsViewset, basename="branch_specialists")
router.register(r"branch_clinics", ClinicSessionsViewset, basename="branch_clinics")
router.register(r"subscriptions", SubscriptionsView, basename="subscriptions")
router.register(r"working_hours", WorkingHoursViewset, basename="working_hours" )
router.register(r"hospital_profile", HospitalProfileViewSet, basename="hospital_profile")
urlpatterns = router.urls

urlpatterns += [
    path( "workspace/", MyWorkspaceView.as_view(), name="workspace" ),
    path( "dashboard/", DashboardView.as_view(), name="dashboard" ),
]


# Branch urls
urlpatterns += [
    path("hosi_dashboard/", BranchDashboardView.as_view(), name="hosi_dashboard" ),
]






