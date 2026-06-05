
from django.urls import path
from .views import MainHomeView, GlobalSearchView

urlpatterns = [
    path("home/", MainHomeView.as_view(), name="home" ),
    path("search/", GlobalSearchView.as_view(), name="search" ),
]

