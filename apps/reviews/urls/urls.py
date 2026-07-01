from django.urls import path
from apps.reviews.views.views import PatientReviewView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("my_reviews", PatientReviewView, basename="my_reviews")
urlpatterns = router.urls




