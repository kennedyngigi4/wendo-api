from django.urls import path
from apps.blogs.views import AllBlogsView

urlpatterns = [
    path( "all/", AllBlogsView.as_view(), name="all"),
]

