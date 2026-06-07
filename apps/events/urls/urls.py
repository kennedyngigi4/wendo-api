from django.urls import path
from apps.events.views.views import AllUpcomingEvents


urlpatterns = [
    path("all/", AllUpcomingEvents.as_view(), name="all"),
]



