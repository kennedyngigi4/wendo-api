from django.urls import path
from apps.services.views.views import AllServicesView, AllSpecialtiesView, ServiceOfferingViewset, AllServiceCategoryView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'offerings', ServiceOfferingViewset, basename="offerings")
urlpatterns = router.urls

urlpatterns += [
    path("categories/", AllServiceCategoryView.as_view(), name="categories", ),
    path("all/", AllServicesView.as_view(), name="all"),
    path("specialties/", AllSpecialtiesView.as_view(), name="specialties"),
]

