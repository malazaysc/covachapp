from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from accounts.views import apply_host_view, guest_inbox, guest_trips, host_dashboard, host_reservations
from core.views import healthcheck
from listings.views import host_listings, listing_availability_partial
from notifications.views import inbox_partial, mark_read_partial
from ops_portal.views import ops_home, ops_hosts, ops_listings, ops_metrics, ops_reservations

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("search.urls")),
    path("accounts/", include("accounts.urls")),
    path("listings/", include("listings.urls")),
    path("reservations/", include("reservations.urls")),
    path("ops/", include("ops_portal.urls")),
    path("ops", ops_home),
    path("ops/hosts", ops_hosts),
    path("ops/listings", ops_listings),
    path("ops/reservations", ops_reservations),
    path("ops/metrics", ops_metrics),
    path("healthz", healthcheck, name="healthcheck"),
    path("host/apply", apply_host_view, name="host_apply"),
    path("host/dashboard", host_dashboard, name="host_dashboard"),
    path("host/listings", host_listings, name="host_listings"),
    path("host/reservations", host_reservations, name="host_reservations"),
    path("guest/trips", guest_trips, name="guest_trips"),
    path("guest/inbox", guest_inbox, name="guest_inbox"),
    path("hx/inbox", inbox_partial, name="hx_inbox"),
    path("hx/inbox/<int:pk>/read", mark_read_partial, name="hx_inbox_read"),
    path("hx/listings/<int:pk>/availability", listing_availability_partial, name="hx_listing_availability"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
