from django.urls import path
from apps.providers.views.branch_views import BranchesViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("branch", BranchesViewSet, basename="branch")
urlpatterns  = router.urls


