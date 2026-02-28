from django.urls import path

from ops_portal.views import (
    approve_host,
    ops_home,
    ops_hosts,
    ops_listings,
    ops_metrics,
    ops_reservations,
    reject_host,
)

app_name = "ops_portal"

urlpatterns = [
    path("", ops_home, name="home"),
    path("hosts/", ops_hosts, name="hosts"),
    path("hosts/<int:pk>/approve/", approve_host, name="approve_host"),
    path("hosts/<int:pk>/reject/", reject_host, name="reject_host"),
    path("listings/", ops_listings, name="listings"),
    path("reservations/", ops_reservations, name="reservations"),
    path("metrics/", ops_metrics, name="metrics"),
]
