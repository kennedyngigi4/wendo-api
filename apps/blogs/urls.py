from django.urls import path
from apps.blogs.views import AllBlogsView, BlogRetrieveView

urlpatterns = [
    path( "all/", AllBlogsView.as_view(), name="all"),
    path( "blogs/<slug:slug>/", BlogRetrieveView.as_view(), name="blog-detail", )
]

