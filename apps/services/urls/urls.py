from django.urls import path
from apps.services.views.views import AllServicesView, AllSpecialtiesView, ServiceOfferingViewset
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'offerings', ServiceOfferingViewset, basename="offerings")
urlpatterns = router.urls

urlpatterns += [
    path("all/", AllServicesView.as_view(), name="all"),
    path("specialties/", AllSpecialtiesView.as_view(), name="specialties"),
]

