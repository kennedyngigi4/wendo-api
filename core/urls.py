from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
]


urlpatterns += [
    path("v1/", include("apps._core_utils.urls")),

    path("v1/account/", include("apps.accounts.urls")),

    path("v1/bookings/", include("apps.bookings.urls.urls")),

    path("v1/blogs/", include("apps.blogs.urls")),

    path("v1/professionals/", include("apps.professionals.urls")),

    path("v1/providers/", include("apps.providers.urls.urls")),
    path("v1/providers/public/", include("apps.providers.urls.public_urls")),

    path( "v1/services/", include("apps.services.urls.urls")),
]


urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

